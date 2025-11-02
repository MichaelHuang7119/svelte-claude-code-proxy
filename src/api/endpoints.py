from fastapi import APIRouter, HTTPException, Request, Header, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime
import uuid
from typing import Optional

from utils.env import config
from src.core.logging import logger
from src.core.client import OpenAIClient
from src.models.claude import ClaudeMessagesRequest, ClaudeTokenCountRequest
from src.conversion.request_converter import convert_claude_to_openai
from src.conversion.response_converter import (
    convert_openai_to_claude_response,
    convert_openai_streaming_to_claude_with_cancellation,
)
from src.core.model_manager import model_manager
from src.core.colored_logger import colored_logger

router = APIRouter()

# Legacy client for fallback (will be replaced by provider manager)
custom_headers = config.get_custom_headers()

openai_client = OpenAIClient(
    config.openai_api_key,
    config.openai_base_url,
    config.request_timeout,
    api_version=config.azure_api_version,
    custom_headers=custom_headers,
)

async def validate_api_key(x_api_key: Optional[str] = Header(None), authorization: Optional[str] = Header(None)):
    """Validate the client's API key from either x-api-key header or Authorization header."""
    client_api_key = None
    
    # Extract API key from headers
    if x_api_key:
        client_api_key = x_api_key
    elif authorization and authorization.startswith("Bearer "):
        client_api_key = authorization.replace("Bearer ", "")
    
    # Skip validation if ANTHROPIC_API_KEY is not set in the environment
    if not config.anthropic_api_key:
        return
        
    # Validate the client API key
    if not client_api_key or not config.validate_client_api_key(client_api_key):
        logger.warning(f"Invalid API key provided by client")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. Please provide a valid Anthropic API key."
        )

async def handle_request_with_fallback(request: ClaudeMessagesRequest, http_request: Request, _: None = Depends(validate_api_key)):
    """Handle request with intelligent fallback logic"""
    try:
        logger.debug(
            f"Processing Claude request: model={request.model}, stream={request.stream}"
        )

        # Generate unique request ID for cancellation tracking
        request_id = str(uuid.uuid4())

        # Get initial client and model from provider manager
        try:
            client_result = await model_manager.get_client_and_model(request.model)
            if not client_result:
                raise HTTPException(status_code=503, detail="No available providers")
        except Exception as e:
            logger.error(f"Failed to get client and model: {e}")
            raise HTTPException(status_code=503, detail=f"Provider error: {str(e)}")
        
        openai_client, model_name, provider_name = client_result

        # Convert Claude request to OpenAI format with the correct model
        openai_request = convert_claude_to_openai(request, model_manager, model_name)

        # Check if client disconnected before processing
        if await http_request.is_disconnected():
            raise HTTPException(status_code=499, detail="Client disconnected")

        if request.stream:
            # Streaming response
            try:
                openai_stream = openai_client.create_chat_completion_stream(
                    openai_request, request_id
                )
                return StreamingResponse(
                    convert_openai_streaming_to_claude_with_cancellation(
                        openai_stream,
                        request,
                        logger,
                        http_request,
                        openai_client,
                        request_id,
                    ),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Headers": "*",
                        "X-Request-ID": request_id,
                        "X-Provider": provider_name,
                    },
                )
            except HTTPException as e:
                # Try fallback logic
                return await try_fallback(request, http_request, _, provider_name, e)
        else:
            # Non-streaming response
            try:
                openai_response = await openai_client.create_chat_completion(
                    openai_request, request_id
                )
                # Mark provider as successful
                if config.provider_manager:
                    config.provider_manager.mark_provider_success(provider_name)
                claude_response = convert_openai_to_claude_response(
                    openai_response, request
                )
                return claude_response
            except HTTPException as e:
                # Try fallback logic
                return await try_fallback(request, http_request, _, provider_name, e)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Unexpected error processing request: {e}")
        logger.error(traceback.format_exc())
        # Try to classify error if we have a client, otherwise use generic message
        try:
            error_message = openai_client.classify_openai_error(str(e))
        except:
            error_message = f"Internal server error: {str(e)}"
        raise HTTPException(status_code=500, detail=error_message)

async def try_fallback(request: ClaudeMessagesRequest, http_request: Request, _, failed_provider: str, error: HTTPException):
    """Try fallback logic: first try other models in same provider, then other providers"""
    logger.error(f"Request failed with {failed_provider}: {error.detail}")
    
    # First, try other models in the same provider
    if config.provider_manager:
        next_model_result = await model_manager.get_next_model_for_provider(request.model, failed_provider)
        if next_model_result:
            colored_logger.warning(f"🔄 Trying next model in {failed_provider}")
            openai_client, model_name, provider_name = next_model_result
            openai_request = convert_claude_to_openai(request, model_manager, model_name)
            
            try:
                if request.stream:
                    openai_stream = openai_client.create_chat_completion_stream(
                        openai_request, str(uuid.uuid4())
                    )
                    return StreamingResponse(
                        convert_openai_streaming_to_claude_with_cancellation(
                            openai_stream,
                            request,
                            logger,
                            http_request,
                            openai_client,
                            str(uuid.uuid4()),
                        ),
                        media_type="text/event-stream",
                        headers={
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                            "Access-Control-Allow-Origin": "*",
                            "Access-Control-Allow-Headers": "*",
                            "X-Request-ID": str(uuid.uuid4()),
                            "X-Provider": provider_name,
                        },
                    )
                else:
                    openai_response = await openai_client.create_chat_completion(
                        openai_request, str(uuid.uuid4())
                    )
                    if config.provider_manager:
                        config.provider_manager.mark_provider_success(provider_name)
                    claude_response = convert_openai_to_claude_response(
                        openai_response, request
                    )
                    return claude_response
            except HTTPException as next_error:
                logger.warning(f"Next model in {failed_provider} also failed: {next_error.detail}")
                # Continue to provider fallback
            except Exception as next_error:
                logger.warning(f"Next model in {failed_provider} failed with exception: {next_error}")
                # Continue to provider fallback
        
        # If no more models in same provider, try other providers
        config.provider_manager.mark_provider_failure(failed_provider, error)
        fallback_result = await model_manager.get_client_and_model(request.model, failed_provider)
        if fallback_result:
            colored_logger.warning(f"🔄 Switching to fallback provider for {request.model}")
            return await handle_request_with_fallback(request, http_request, _)
    
    # If all fallbacks failed, return the original error
    import traceback
    logger.error(traceback.format_exc())
    try:
        error_message = openai_client.classify_openai_error(error.detail)
    except:
        error_message = str(error.detail)
    error_response = {
        "type": "error",
        "error": {"type": "api_error", "message": error_message},
    }
    return JSONResponse(status_code=error.status_code, content=error_response)

@router.post("/v1/messages")
async def create_message(request: ClaudeMessagesRequest, http_request: Request, _: None = Depends(validate_api_key)):
    """Create message with intelligent fallback logic"""
    return await handle_request_with_fallback(request, http_request, _)


@router.post("/v1/messages/count_tokens")
async def count_tokens(request: ClaudeTokenCountRequest, _: None = Depends(validate_api_key)):
    try:
        # For token counting, we'll use a simple estimation
        # In a real implementation, you might want to use tiktoken or similar

        total_chars = 0

        # Count system message characters
        if request.system:
            if isinstance(request.system, str):
                total_chars += len(request.system)
            elif isinstance(request.system, list):
                for block in request.system:
                    if hasattr(block, "text"):
                        total_chars += len(block.text)

        # Count message characters
        for msg in request.messages:
            if msg.content is None:
                continue
            elif isinstance(msg.content, str):
                total_chars += len(msg.content)
            elif isinstance(msg.content, list):
                for block in msg.content:
                    if hasattr(block, "text") and block.text is not None:
                        total_chars += len(block.text)

        # Rough estimation: 4 characters per token
        estimated_tokens = max(1, total_chars // 4)

        return {"input_tokens": estimated_tokens}

    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = "healthy"
    
    # Check provider manager status if available
    provider_status = {}
    if config.provider_manager:
        provider_status = config.provider_manager.get_provider_status_summary()
        # Check if any providers are healthy
        healthy_providers = [p for p in provider_status.values() if p["status"] == "healthy"]
        if not healthy_providers:
            health_status = "unhealthy"
    
    return {
        "status": health_status,
        "timestamp": datetime.now().isoformat(),
        "openai_api_configured": bool(config.openai_api_key),
        "api_key_valid": config.validate_api_key(),
        "client_api_key_validation": bool(config.anthropic_api_key),
        "providers": provider_status,
    }


@router.get("/test-connection")
async def test_connection():
    """Test API connectivity to available providers"""
    try:
        # Try to get a client from provider manager first
        if config.provider_manager:
            # Get a small model client for testing
            client_result = await model_manager.get_client_and_model("claude-3-5-haiku-20241022")
            if client_result:
                test_client, model_name, provider_name = client_result
                test_response = await test_client.create_chat_completion(
                    {
                        "model": model_name,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 5,
                    }
                )
                
                return {
                    "status": "success",
                    "message": f"Successfully connected to {provider_name} API",
                    "model_used": model_name,
                    "provider": provider_name,
                    "timestamp": datetime.now().isoformat(),
                    "response_id": test_response.get("id", "unknown"),
                }
        
        # Fallback to legacy client
        test_response = await openai_client.create_chat_completion(
            {
                "model": config.small_model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5,
            }
        )

        return {
            "status": "success",
            "message": "Successfully connected to OpenAI API (legacy mode)",
            "model_used": config.small_model,
            "provider": "legacy",
            "timestamp": datetime.now().isoformat(),
            "response_id": test_response.get("id", "unknown"),
        }

    except Exception as e:
        logger.error(f"API connectivity test failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "failed",
                "error_type": "API Error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
                "suggestions": [
                    "Check your API keys are valid",
                    "Verify your API keys have the necessary permissions",
                    "Check if you have reached rate limits",
                    "Ensure at least one provider is configured and healthy",
                ],
            },
        )


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Claude-to-OpenAI API Proxy v1.0.0",
        "status": "running",
        "config": {
            "openai_base_url": config.openai_base_url,
            "max_tokens_limit": config.max_tokens_limit,
            "api_key_configured": bool(config.openai_api_key),
            "client_api_key_validation": bool(config.anthropic_api_key),
            "big_model": config.big_model,
            "small_model": config.small_model,
        },
        "endpoints": {
            "messages": "/v1/messages",
            "count_tokens": "/v1/messages/count_tokens",
            "health": "/health",
            "test_connection": "/test-connection",
        },
    }
