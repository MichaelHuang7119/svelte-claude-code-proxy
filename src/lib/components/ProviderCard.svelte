<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { ProviderConfig, HealthCheckResponse, ProviderStatusInfo } from '$lib/types/config';
	import { goto } from '$app/navigation';
	import { providersStore } from '$lib/stores/providers';
	import { configStore } from '$lib/stores/config';
	import HealthIndicator from './HealthIndicator.svelte';

	let { provider } = $props<{ provider: ProviderConfig }>();

	let testing = $state(false);
	let testResult = $state<string | null>(null);
	let storeLoading = $state(false);
	
	// Create reactive state for health data
	let health = $state<HealthCheckResponse | null>(null);
	let healthInfo = $state<ProviderStatusInfo | null>(null);

	// Subscribe to health store
	$effect(() => {
		const unsubscribe = providersStore.health.subscribe((value) => {
			health = value;
			// Update healthInfo when health changes
			if (value) {
				healthInfo = value.providers[provider.name] || null;
			} else {
				healthInfo = null;
			}
		});
		return unsubscribe;
	});

	// Subscribe to loading store
	$effect(() => {
		const unsubscribe = providersStore.loading.subscribe((value) => {
			storeLoading = value;
		});
		return unsubscribe;
	});

	// Derive status from health data
	const status = $derived(
		health?.providers[provider.name]?.status || 'unhealthy'
	);

	async function handleTest() {
		testing = true;
		testResult = null;
		try {
			const result = await providersStore.testProvider(provider.name);
			testResult = result.status === 'success' ? 'Connection successful!' : result.message;
		} catch (err) {
			testResult = err instanceof Error ? err.message : 'Test failed';
		} finally {
			testing = false;
		}
	}

	async function handleToggle() {
		try {
			await providersStore.toggleProvider(provider.name, !provider.enabled);
		} catch (err) {
			console.error('Failed to toggle provider:', err);
		}
	}

	function handleEdit() {
		goto(`/providers/${encodeURIComponent(provider.name)}`);
	}

	async function handleDelete() {
		if (confirm(`Are you sure you want to delete provider "${provider.name}"?`)) {
			const { get } = await import('svelte/store');
			const currentConfig = get(configStore.config);
			
			if (currentConfig && currentConfig.providers.length === 1) {
				alert('Cannot delete the last provider. At least one provider is required.');
				return;
			}
			
			configStore.removeProvider(provider.name);
			const success = await configStore.save();
			
			if (success) {
				testResult = 'Provider deleted successfully';
			} else {
				const errorValue = get(configStore.error);
				alert(errorValue || 'Failed to delete provider');
			}
		}
	}
</script>

<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
	<div class="flex items-start justify-between mb-4">
		<div class="flex-1">
			<div class="flex items-center gap-3 mb-2">
				<h3 class="text-lg font-semibold text-gray-900">{provider.name}</h3>
				<HealthIndicator status={status} />
				{#if !provider.enabled}
					<span class="px-2 py-1 text-xs font-medium text-gray-500 bg-gray-100 rounded">Disabled</span>
				{/if}
			</div>
			<div class="text-sm text-gray-600 space-y-1">
				<div>
					<span class="font-medium">Priority:</span> {provider.priority}
				</div>
				<div>
					<span class="font-medium">Base URL:</span>
					<span class="font-mono text-xs">{provider.base_url}</span>
				</div>
				{#if healthInfo}
					<div class="text-xs text-gray-500 mt-2">
						Failures: {healthInfo.failure_count} | Last success:
						{healthInfo.last_success
							? new Date(healthInfo.last_success * 1000).toLocaleString()
							: 'Never'}
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="mb-4">
		<div class="text-sm font-medium text-gray-700 mb-2">Models:</div>
		<div class="grid grid-cols-3 gap-2 text-xs">
			<div>
				<span class="font-medium text-gray-600">Big:</span>
				<div class="text-gray-500">{provider.models.big.length} models</div>
			</div>
			<div>
				<span class="font-medium text-gray-600">Middle:</span>
				<div class="text-gray-500">{provider.models.middle.length} models</div>
			</div>
			<div>
				<span class="font-medium text-gray-600">Small:</span>
				<div class="text-gray-500">{provider.models.small.length} models</div>
			</div>
		</div>
	</div>

	{#if testResult}
		<div
			class="mb-3 p-2 text-sm rounded {testResult.includes('successful')
				? 'bg-green-50 text-green-700'
				: 'bg-red-50 text-red-700'}"
		>
			{testResult}
		</div>
	{/if}

	<div class="flex items-center gap-2">
		<button
			onclick={handleEdit}
			class="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
		>
			Edit
		</button>
		<button
			onclick={handleToggle}
			class="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
			disabled={storeLoading}
		>
			{provider.enabled ? 'Disable' : 'Enable'}
		</button>
		<button
			onclick={handleTest}
			class="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
			disabled={testing || storeLoading}
		>
			{testing ? 'Testing...' : 'Test'}
		</button>
		<button
			onclick={handleDelete}
			class="px-3 py-2 text-sm font-medium text-red-700 bg-red-50 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
		>
			Delete
		</button>
	</div>
</div>
