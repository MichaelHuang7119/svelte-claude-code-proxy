/**
 * TypeScript 类型定义，基于 providers.example.json 结构
 */

export interface ProviderModelConfig {
	big: string[];
	middle: string[];
	small: string[];
}

export interface ProviderConfig {
	name: string;
	enabled: boolean;
	priority: number;
	api_key: string;
	base_url: string;
	api_version: string | null;
	timeout: number;
	max_retries: number;
	custom_headers: Record<string, string>;
	models: ProviderModelConfig;
}

export interface CircuitBreakerConfig {
	failure_threshold: number;
	recovery_timeout: number;
}

export type FallbackStrategy = 'priority' | 'round_robin' | 'random';

export interface ProviderManagerConfig {
	providers: ProviderConfig[];
	fallback_strategy: FallbackStrategy;
	health_check_interval: number;
	circuit_breaker: CircuitBreakerConfig;
}

/**
 * Provider 状态相关类型
 */
export type ProviderStatus = 'healthy' | 'unhealthy' | 'circuit_open';

export interface ProviderStatusInfo {
	status: ProviderStatus;
	priority: number;
	failure_count: number;
	last_failure: number | null;
	last_success: number | null;
	models: ProviderModelConfig;
}

export interface HealthCheckResponse {
	status: string;
	timestamp: string;
	openai_api_configured: boolean;
	api_key_valid: boolean;
	client_api_key_validation: boolean;
	providers: Record<string, ProviderStatusInfo>;
}

/**
 * API 响应类型
 */
export interface ApiResponse<T> {
	data?: T;
	error?: string;
	message?: string;
}

/**
 * 测试连接响应
 */
export interface TestConnectionResponse {
	status: 'success' | 'failed';
	message: string;
	model_used?: string;
	provider?: string;
	timestamp: string;
	error_type?: string;
	suggestions?: string[];
}
