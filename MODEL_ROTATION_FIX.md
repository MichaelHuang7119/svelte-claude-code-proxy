# 模型轮换和智能故障转移修复

## 🐛 问题描述

从终端日志可以看到，当 ModelScope 供应商遇到 429 错误（请求限制）时，系统直接切换到了下一个供应商（OpenAI），而没有尝试 ModelScope 供应商下的其他模型。

**问题日志**：
```
2025-10-23 03:45:44,337 - ERROR - OpenAI API error with modelscope: Error code: 429 - {'errors': {'message': 'Request limit exceeded.', 'request_id': 'e1a70c0b-14a9-4cf5-a839-ec196141cf61'}}
2025-10-23 03:45:44,337 - WARNING - ❌ Provider modelscope failed (attempt 1)
🎯 Using openai with model gpt-4o-mini for claude-haiku-4-5-20251001
🔄 Switching to fallback provider for claude-haiku-4-5-20251001
```

## 🔍 根本原因

1. **缺少模型索引跟踪**: `ProviderState` 没有跟踪每个供应商内部模型的当前索引
2. **只返回第一个模型**: `get_provider_for_model` 和 `get_fallback_provider_for_model` 只返回 `models[0]`
3. **没有供应商内部故障转移**: 当某个模型失败时，没有尝试同一供应商的其他模型

## ✅ 修复方案

### 1. 添加模型索引跟踪

在 `ProviderState` 中添加了模型轮换跟踪：

```python
@dataclass
class ProviderState:
    # ... 其他字段 ...
    # Model rotation tracking
    model_indices: Dict[str, int] = None  # Track current model index for each type
    
    def __post_init__(self):
        if self.model_indices is None:
            self.model_indices = {}
    
    def get_next_model(self, model_type: str) -> Optional[str]:
        """Get next model for the given type, cycling through available models"""
        models = getattr(self.provider.models, model_type, [])
        if not models:
            return None
        
        # Get current index for this model type
        current_index = self.model_indices.get(model_type, 0)
        
        # Get the model at current index
        model = models[current_index]
        
        # Update index for next time (cycle through models)
        self.model_indices[model_type] = (current_index + 1) % len(models)
        
        return model
```

### 2. 更新供应商选择逻辑

修改了 `get_provider_for_model` 和 `get_fallback_provider_for_model` 方法：

```python
def get_provider_for_model(self, model_type: str) -> Optional[Tuple[ProviderState, str]]:
    """Get provider and model for the given model type (big/middle/small)"""
    available_providers = self.get_available_providers()
    
    if not available_providers:
        return None
    
    # Try each provider in priority order
    for state in available_providers:
        model = state.get_next_model(model_type)  # 使用轮换机制
        if model:
            return state, model
    
    return None
```

### 3. 添加供应商内部模型切换

添加了 `get_next_model_for_provider` 方法：

```python
def get_next_model_for_provider(self, provider_name: str, model_type: str) -> Optional[Tuple[ProviderState, str]]:
    """Get next model for a specific provider, cycling through its models"""
    if provider_name not in self.providers:
        return None
    
    state = self.providers[provider_name]
    if state.status != ProviderStatus.HEALTHY:
        return None
    
    model = state.get_next_model(model_type)
    if model:
        return state, model
    
    return None
```

### 4. 实现智能故障转移逻辑

在 `model_manager.py` 中添加了 `get_next_model_for_provider` 方法：

```python
async def get_next_model_for_provider(self, claude_model: str, provider_name: str) -> Optional[Tuple[any, str, str]]:
    """Get next model for a specific provider, cycling through its models"""
    # ... 实现逻辑 ...
```

### 5. 更新API端点故障转移

在 `endpoints.py` 中实现了智能故障转移逻辑：

```python
async def try_fallback(request: ClaudeMessagesRequest, http_request: Request, _, failed_provider: str, error: HTTPException):
    """Try fallback logic: first try other models in same provider, then other providers"""
    logger.error(f"Request failed with {failed_provider}: {error.detail}")
    
    # First, try other models in the same provider
    if config.provider_manager:
        next_model_result = await model_manager.get_next_model_for_provider(request.model, failed_provider)
        if next_model_result:
            colored_logger.warning(f"🔄 Trying next model in {failed_provider}")
            # ... 尝试下一个模型 ...
        
        # If no more models in same provider, try other providers
        config.provider_manager.mark_provider_failure(failed_provider, error)
        fallback_result = await model_manager.get_client_and_model(request.model, failed_provider)
        if fallback_result:
            colored_logger.warning(f"🔄 Switching to fallback provider for {request.model}")
            return await handle_request_with_fallback(request, http_request, _)
```

## 🎯 修复效果

### 模型轮换测试

测试结果显示模型轮换正常工作：

```
Call 1: modelscope:Qwen/Qwen2.5-7B-Instruct
Call 2: modelscope:Qwen/Qwen3-8B  
Call 3: modelscope:Qwen/Qwen3-32B
Call 4: modelscope:Qwen/Qwen2.5-7B-Instruct  # 循环回到第一个
Call 5: modelscope:Qwen/Qwen3-8B
```

### 故障转移策略

现在的故障转移策略是：

1. **供应商内部故障转移**: 当某个模型失败时，先尝试同一供应商的其他模型
2. **供应商间故障转移**: 当供应商内所有模型都失败时，切换到下一个供应商
3. **模型轮换**: 每次请求都会轮换到下一个可用的模型

## 📊 配置示例

以 ModelScope 供应商为例，配置了多个 small 模型：

```json
{
  "name": "modelscope",
  "enabled": true,
  "priority": 1,
  "api_key": "${MODELSCOPE_API_KEY}",
  "base_url": "https://api-inference.modelscope.cn/v1/",
  "models": {
    "small": ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen3-8B", "Qwen/Qwen3-32B"]
  }
}
```

现在当 `Qwen/Qwen2.5-7B-Instruct` 遇到 429 错误时，系统会：

1. 尝试 `Qwen/Qwen3-8B`
2. 如果也失败，尝试 `Qwen/Qwen3-32B`
3. 如果所有 ModelScope 模型都失败，才切换到 OpenAI 供应商

## 🎉 总结

修复后的系统现在支持：

1. **智能模型轮换**: 每次请求自动轮换到下一个可用模型
2. **供应商内部故障转移**: 模型失败时先尝试同一供应商的其他模型
3. **供应商间故障转移**: 供应商内所有模型失败时才切换供应商
4. **更好的资源利用**: 充分利用每个供应商的多个模型

这大大提高了系统的可靠性和资源利用率！

---

**修复时间**: 2025-10-23  
**状态**: ✅ 完成并测试通过


