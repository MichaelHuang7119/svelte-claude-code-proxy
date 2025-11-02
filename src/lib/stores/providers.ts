/**
 * Provider 状态管理 Store
 */

import { writable } from 'svelte/store';
import type { HealthCheckResponse, ProviderStatusInfo } from '$lib/types/config';
import { api } from '../api/client';
import { configStore } from './config';

class ProvidersStore {
	health = writable<HealthCheckResponse | null>(null);
	loading = writable(false);
	error = writable<string | null>(null);
	pollInterval: number | null = null;
	pollIntervalMs = 5000; // 5 秒轮询

	/**
	 * 获取 provider 状态
	 */
	getProviderStatus(name: string): ProviderStatusInfo | null {
		// Use get() to read from store synchronously (for SSR compatibility)
		const { get } = require('svelte/store');
		const currentHealth = get(this.health);
		if (!currentHealth) return null;
		return currentHealth.providers[name] || null;
	}

	/**
	 * 检查 provider 是否健康
	 */
	isHealthy(name: string): boolean {
		const status = this.getProviderStatus(name);
		return status?.status === 'healthy' || false;
	}

	/**
	 * 加载健康状态
	 */
	async loadHealth() {
		this.loading.set(true);
		this.error.set(null);
		try {
			const healthData = await api.getHealth();
			this.health.set(healthData);
			// Clear error on success
			this.error.set(null);
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to load health status';
			this.error.set(errorMessage);
			console.error('Failed to load health:', err);
			// Keep previous health data on error (don't clear it)
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * 开始轮询健康状态
	 */
	startPolling() {
		if (this.pollInterval) {
			return; // 已经在轮询
		}

		// 立即加载一次（不等待，异步执行）
		this.loadHealth().catch((err) => {
			console.error('Initial health check failed:', err);
		});

		// 设置轮询
		this.pollInterval = window.setInterval(() => {
			this.loadHealth().catch((err) => {
				console.error('Polling health check failed:', err);
			});
		}, this.pollIntervalMs);
	}

	/**
	 * 停止轮询
	 */
	stopPolling() {
		if (this.pollInterval) {
			clearInterval(this.pollInterval);
			this.pollInterval = null;
		}
	}

	/**
	 * 测试 provider 连接
	 */
	async testProvider(name: string) {
		this.loading.set(true);
		this.error.set(null);
		try {
			const result = await api.testProvider(name);
			// 测试后刷新健康状态
			await this.loadHealth();
			return result;
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to test provider';
			this.error.set(errorMessage);
			console.error('Failed to test provider:', err);
			throw err;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * 启用/禁用 provider（临时，不修改文件）
	 */
	async toggleProvider(name: string, enabled: boolean) {
		this.loading.set(true);
		this.error.set(null);
		try {
			await api.toggleProvider(name, enabled);
			// 更新本地配置状态
			const { get } = await import('svelte/store');
			const currentConfig = get(configStore.config);
			if (currentConfig) {
				const provider = currentConfig.providers.find((p) => p.name === name);
				if (provider) {
					provider.enabled = enabled;
					configStore.config.set(currentConfig); // Update store
				}
			}
			// 刷新健康状态
			await this.loadHealth();
		} catch (err) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to toggle provider';
			this.error.set(errorMessage);
			console.error('Failed to toggle provider:', err);
			throw err;
		} finally {
			this.loading.set(false);
		}
	}

	/**
	 * 清除错误
	 */
	clearError() {
		this.error.set(null);
	}
}

export const providersStore = new ProvidersStore();