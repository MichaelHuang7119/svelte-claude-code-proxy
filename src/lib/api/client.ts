/**
 * API 客户端封装
 * 统一的请求封装、错误处理、基础 URL 配置
 */

import type {
	ProviderManagerConfig,
	HealthCheckResponse,
	TestConnectionResponse,
	ApiResponse
} from '$lib/types/config';

// Determine API base URL based on environment
// In browser: use relative URLs (server-side proxy) or absolute URL if provided
// In server: use Docker internal address or absolute URL
const getApiBaseUrl = () => {
	// Access VITE env var (available in both client and server during build)
	const envUrl = (import.meta as any).env?.VITE_API_BASE_URL || '';
	
	// If running in browser and URL is Docker internal address, use relative path (server proxy)
	if (typeof window !== 'undefined') {
		if (envUrl.includes('backend:') || envUrl === '') {
			return '';
		}
		return envUrl;
	}
	
	// Server-side: use Docker internal address
	return envUrl || 'http://backend:8082';
};

const API_BASE_URL = getApiBaseUrl();

class ApiError extends Error {
	constructor(
		public status: number,
		public statusText: string,
		message: string,
		public data?: unknown
	) {
		super(message);
		this.name = 'ApiError';
	}
}

/**
 * 通用请求函数
 */
async function request<T>(
	endpoint: string,
	options: RequestInit = {}
): Promise<T> {
	// Use relative URL (via Vite proxy) if API_BASE_URL is empty, otherwise use absolute URL
	const url = API_BASE_URL ? `${API_BASE_URL}${endpoint}` : endpoint;
	
	console.log('[API Client] Making request:', { url, method: options.method || 'GET', endpoint, API_BASE_URL });
	
	const defaultHeaders: HeadersInit = {
		'Content-Type': 'application/json'
	};

	const config: RequestInit = {
		...options,
		headers: {
			...defaultHeaders,
			...options.headers
		}
	};

	try {
		const response = await fetch(url, config);
		console.log('[API Client] Response:', { 
			status: response.status, 
			statusText: response.statusText,
			ok: response.ok,
			url: response.url 
		});

		if (!response.ok) {
			let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
			let errorData: unknown = null;

			try {
				const errorBody = await response.json();
				errorMessage = errorBody.message || errorBody.error || errorMessage;
				errorData = errorBody;
			} catch {
				// 如果响应不是 JSON，使用默认错误信息
				const text = await response.text();
				if (text) {
					errorMessage = text;
				}
			}

			console.error('[API Client] Request failed:', { status: response.status, errorMessage, errorData });
			throw new ApiError(response.status, response.statusText, errorMessage, errorData);
		}

		// 处理空响应
		const contentType = response.headers.get('content-type');
		if (!contentType || !contentType.includes('application/json')) {
			console.warn('[API Client] Response is not JSON, returning empty object');
			return {} as T;
		}

		const data = await response.json();
		console.log('[API Client] Request successful, data received');
		return data;
	} catch (error) {
		console.error('[API Client] Request error:', error);
		if (error instanceof ApiError) {
			throw error;
		}
		throw new ApiError(0, 'NetworkError', error instanceof Error ? error.message : 'Network request failed');
	}
}

/**
 * API 客户端
 */
export const api = {
	/**
	 * 获取健康状态
	 */
	async getHealth(): Promise<HealthCheckResponse> {
		return request<HealthCheckResponse>('/health');
	},

	/**
	 * 测试连接
	 */
	async testConnection(): Promise<TestConnectionResponse> {
		return request<TestConnectionResponse>('/test-connection');
	},

	/**
	 * 测试特定 provider 连接
	 */
	async testProvider(name: string): Promise<TestConnectionResponse> {
		return request<TestConnectionResponse>(`/api/providers/${encodeURIComponent(name)}/test`, {
			method: 'POST'
		});
	},

	/**
	 * 获取配置
	 */
	async getConfig(): Promise<ProviderManagerConfig> {
		return request<ProviderManagerConfig>('/api/config/providers');
	},

	/**
	 * 保存配置
	 */
	async saveConfig(config: ProviderManagerConfig): Promise<ApiResponse<ProviderManagerConfig>> {
		return request<ApiResponse<ProviderManagerConfig>>('/api/config/providers', {
			method: 'PUT',
			body: JSON.stringify(config)
		});
	},

	/**
	 * 重载配置
	 */
	async reloadConfig(): Promise<ApiResponse<void>> {
		return request<ApiResponse<void>>('/api/config/reload', {
			method: 'POST'
		});
	},

	/**
	 * 启用/禁用 provider
	 */
	async toggleProvider(name: string, enabled: boolean): Promise<ApiResponse<void>> {
		return request<ApiResponse<void>>(`/api/providers/${encodeURIComponent(name)}/toggle`, {
			method: 'PUT',
			body: JSON.stringify({ enabled })
		});
	},

	/**
	 * 获取所有 providers 详细信息
	 */
	async getProviders(): Promise<ProviderManagerConfig> {
		return request<ProviderManagerConfig>('/api/providers');
	}
};

export { ApiError };
