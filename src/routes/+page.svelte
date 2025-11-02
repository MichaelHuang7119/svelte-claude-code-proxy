<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import { configStore } from '$lib/stores/config';
	import { providersStore } from '$lib/stores/providers';
	import ProviderCard from '$lib/components/ProviderCard.svelte';

	let { data } = $props();

	import type { ProviderManagerConfig } from '$lib/types/config';

	let saving = $state(false);
	let saveMessage = $state<string | null>(null);
	
	// Create reactive state variables
	let config = $state<ProviderManagerConfig | null>(null);
	let loading = $state(false);
	let error = $state<string | null>(null);

	// Subscribe to stores reactively
	$effect(() => {
		const unsubscribeConfig = configStore.config.subscribe((value) => {
			config = value;
		});
		const unsubscribeLoading = configStore.loading.subscribe((value) => {
			loading = value;
		});
		const unsubscribeError = configStore.error.subscribe((value) => {
			error = value;
		});

		return () => {
			unsubscribeConfig();
			unsubscribeLoading();
			unsubscribeError();
		};
	});

	// Initialize config from server data if available
	$effect(() => {
		if (data?.config) {
			configStore.config.set(data.config);
			configStore.error.set(null);
			configStore.loading.set(false);
		}
		if (data?.error) {
			configStore.error.set(data.error);
		}
	});

	onMount(async () => {
		// Always try to load config on mount to ensure fresh data
		// This handles both initial load and refresh cases
		await configStore.load();
		providersStore.startPolling();
	});

	onDestroy(() => {
		providersStore.stopPolling();
	});

	async function handleSave() {
		saving = true;
		saveMessage = null;

		// 验证配置
		const validation = configStore.validate();
		if (!validation.valid) {
			saveMessage = `Validation failed: ${validation.errors.join(', ')}`;
			saving = false;
			return;
		}

		const success = await configStore.save();
		if (success) {
			saveMessage = 'Configuration saved successfully!';
			setTimeout(() => {
				saveMessage = null;
			}, 3000);
		} else {
			saveMessage = error || 'Failed to save configuration';
		}

		saving = false;
	}

	function handleAddProvider() {
		goto('/providers/+new');
	}

	function handleGlobalConfig() {
		goto('/config');
	}
</script>

<div class="container mx-auto px-4 py-8">
	<div class="mb-6 flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Provider Management</h1>
			<p class="mt-2 text-sm text-gray-600">
				Manage your LLM providers and their configurations
			</p>
		</div>
		<div class="flex gap-3">
			<button
				onclick={handleGlobalConfig}
				class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
			>
				Global Config
			</button>
			<button
				onclick={handleAddProvider}
				class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
			>
				+ Add Provider
			</button>
			<button
				onclick={handleSave}
				disabled={saving || loading || !config}
				class="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
			>
				{saving ? 'Saving...' : 'Save All'}
			</button>
		</div>
	</div>

	{#if saveMessage}
		<div
			class="mb-4 p-4 rounded-md {saveMessage.includes('success')
				? 'bg-green-50 text-green-700 border border-green-200'
				: 'bg-red-50 text-red-700 border border-red-200'}"
		>
			{saveMessage}
		</div>
	{/if}

	{#if (error || data?.error) && !loading}
		<div class="mb-4 p-4 bg-red-50 text-red-700 border border-red-200 rounded-md">
			<p class="font-medium mb-2">Error loading configuration:</p>
			<p class="mb-2">{error || data?.error}</p>
			<button
				onclick={async () => await configStore.load()}
				class="px-3 py-1 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700"
			>
				Retry
			</button>
		</div>
	{/if}

	{#if loading && !config}
		<div class="flex items-center justify-center py-12">
			<div class="text-gray-500">Loading configuration...</div>
		</div>
	{:else if config}
		{#if config.providers.length === 0}
			<div class="text-center py-12 bg-white rounded-lg border border-gray-200">
				<p class="text-gray-500 mb-4">No providers configured</p>
				<button
					onclick={handleAddProvider}
					class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
				>
					Add Your First Provider
				</button>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
				{#each config.providers as provider}
					<ProviderCard {provider} />
				{/each}
			</div>
		{/if}
	{:else if error}
		<div class="text-center py-12 bg-white rounded-lg border border-gray-200">
			<p class="text-red-600 mb-2 font-medium">Unable to load configuration</p>
			<p class="text-gray-500 mb-4 text-sm">{error}</p>
			<button
				onclick={async () => {
					configStore.clearError();
					await configStore.load();
				}}
				class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
			>
				Retry Loading
			</button>
		</div>
	{:else}
		<div class="text-center py-12 bg-white rounded-lg border border-gray-200">
			<p class="text-gray-500 mb-4">No configuration loaded</p>
			<button
				onclick={async () => await configStore.load()}
				class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
			>
				Load Configuration
			</button>
		</div>
	{/if}
</div>