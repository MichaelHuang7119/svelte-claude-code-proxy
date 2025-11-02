/**
 * 配置状态管理 Store
 */

import { browser } from '$app/environment';
import { writable, get } from 'svelte/store';
import type { ProviderManagerConfig, ProviderConfig } from '$lib/types/config';
import { api } from '../api/client';

// Use Svelte stores instead of state() for SSR compatibility
class ConfigStore {
	config = writable<ProviderManagerConfig | null>(null);
	loading = writable(false);
	error = writable<string | null>(null);
	lastSaved = writable<Date | null>(null);

	/**
	 * 加载配置
	 */
	async load() {
		this.loading.set(true);
		this.error.set(null);
		try {
			console.log('[ConfigStore] Loading config from API...');
			const configData = await api.getConfig();
			this.config.set(configData);
			console.log('[ConfigStore] Config loaded successfully:', configData);
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to load config';
			console.error('[ConfigStore] Failed to load config:', err);
			console.error('[ConfigStore] Error details:', {
				message: errorMessage,
				type: err?.constructor?.name,
				stack: err instanceof Error ? err.stack : undefined
			});
			this.error.set(errorMessage);
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * 保存配置
	 */
	async save(): Promise<boolean> {
		const currentConfig = get(this.config);
		if (!currentConfig) {
			this.error.set('No config to save');
			return false;
		}

		this.loading.set(true);
		this.error.set(null);

		try {
			// 保存配置
			const response = await api.saveConfig(currentConfig);
			
			if (response.error) {
				throw new Error(response.error);
			}

			// 重载配置
			const reloadResponse = await api.reloadConfig();
			
			if (reloadResponse.error) {
				throw new Error(reloadResponse.error || 'Failed to reload config');
			}

			this.lastSaved.set(new Date());
			
			// 重新加载以获取最新状态
			await this.load();
			
			return true;
		} catch (err) {
			this.error.set(err instanceof Error ? err.message : 'Failed to save config');
			console.error('Failed to save config:', err);
			return false;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * 添加 provider
	 */
	addProvider(provider: ProviderConfig) {
		const currentConfig = get(this.config);
		if (!currentConfig) return;
		
		currentConfig.providers.push(provider);
		// 按优先级排序
		currentConfig.providers.sort((a: ProviderConfig, b: ProviderConfig) => a.priority - b.priority);
		this.config.set(currentConfig);
	}

	/**
	 * 更新 provider
	 */
	updateProvider(name: string, updates: Partial<ProviderConfig>) {
		const currentConfig = get(this.config);
		if (!currentConfig) return;
		
		const index = currentConfig.providers.findIndex((p: ProviderConfig) => p.name === name);
		if (index !== -1) {
			currentConfig.providers[index] = { ...currentConfig.providers[index], ...updates };
			// 按优先级排序
			currentConfig.providers.sort((a: ProviderConfig, b: ProviderConfig) => a.priority - b.priority);
			this.config.set(currentConfig);
		}
	}

	/**
	 * 删除 provider
	 */
	removeProvider(name: string) {
		const currentConfig = get(this.config);
		if (!currentConfig) return;
		
		const index = currentConfig.providers.findIndex((p: ProviderConfig) => p.name === name);
		if (index !== -1) {
			currentConfig.providers.splice(index, 1);
			this.config.set(currentConfig);
		}
	}

	/**
	 * 获取 provider
	 */
	getProvider(name: string): ProviderConfig | undefined {
		const currentConfig = get(this.config);
		if (!currentConfig) return undefined;
		return currentConfig.providers.find((p) => p.name === name);
	}

	/**
	 * 更新全局配置
	 */
	updateGlobalConfig(updates: Partial<ProviderManagerConfig>) {
		const currentConfig = get(this.config);
		if (!currentConfig) return;
		
		this.config.set({
			...currentConfig,
			...updates
		});
	}

	/**
	 * 验证配置
	 */
	validate(): { valid: boolean; errors: string[] } {
		const errors: string[] = [];
		const currentConfig = get(this.config);

		if (!currentConfig) {
			errors.push('Config is null');
			return { valid: false, errors };
		}

		// 验证至少有一个 provider
		if (currentConfig.providers.length === 0) {
			errors.push('At least one provider is required');
		}

		// 验证每个 provider
		currentConfig.providers.forEach((provider, index) => {
			if (!provider.name || provider.name.trim() === '') {
				errors.push(`Provider ${index + 1}: name is required`);
			}

			if (!provider.api_key || provider.api_key.trim() === '') {
				errors.push(`Provider ${provider.name || index + 1}: api_key is required`);
			}

			if (!provider.base_url || provider.base_url.trim() === '') {
				errors.push(`Provider ${provider.name || index + 1}: base_url is required`);
			}

			// 验证 URL 格式
			try {
				new URL(provider.base_url);
			} catch {
				errors.push(`Provider ${provider.name || index + 1}: base_url is not a valid URL`);
			}

			// 验证至少有一个模型类型有模型
			const hasModels =
				provider.models.big.length > 0 ||
				provider.models.middle.length > 0 ||
				provider.models.small.length > 0;

			if (!hasModels) {
				errors.push(
					`Provider ${provider.name || index + 1}: at least one model is required (big, middle, or small)`
				);
			}

			// 验证 big 类型至少有一个模型（必需）
			if (provider.models.big.length === 0) {
				errors.push(`Provider ${provider.name || index + 1}: big models list cannot be empty`);
			}

			// 验证 priority 为正整数
			if (provider.priority <= 0 || !Number.isInteger(provider.priority)) {
				errors.push(
					`Provider ${provider.name || index + 1}: priority must be a positive integer`
				);
			}

			// 验证 timeout 为正整数
			if (provider.timeout <= 0 || !Number.isInteger(provider.timeout)) {
				errors.push(
					`Provider ${provider.name || index + 1}: timeout must be a positive integer`
				);
			}

			// 验证 max_retries 为非负整数
			if (provider.max_retries < 0 || !Number.isInteger(provider.max_retries)) {
				errors.push(
					`Provider ${provider.name || index + 1}: max_retries must be a non-negative integer`
				);
			}
		});

		// 验证至少有一个启用的 provider
		const enabledProviders = currentConfig.providers.filter((p) => p.enabled);
		if (enabledProviders.length === 0) {
			errors.push('At least one provider must be enabled');
		}

		return {
			valid: errors.length === 0,
			errors
		};
	}

	/**
	 * 重置错误状态
	 */
	clearError() {
		this.error.set(null);
	}
}

export const configStore = new ConfigStore();