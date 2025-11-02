<script lang="ts">
	import { goto } from '$app/navigation';
	import type { FallbackStrategy, ProviderManagerConfig } from '$lib/types/config';
	import { configStore } from '$lib/stores/config';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';

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

	onMount(async () => {
		const currentConfig = get(configStore.config);
		if (!currentConfig) {
			await configStore.load();
		}
	});

	const fallbackStrategies: FallbackStrategy[] = ['priority', 'round_robin', 'random'];

	async function handleSave() {
		saving = true;
		saveMessage = null;

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
</script>

<div class="container mx-auto px-4 py-8 max-w-4xl">
	<div class="mb-6">
		<button
			onclick={() => goto('/')}
			class="mb-4 text-sm text-blue-600 hover:text-blue-700"
		>
			← Back to Providers
		</button>
		<h1 class="text-3xl font-bold text-gray-900">Global Configuration</h1>
		<p class="mt-2 text-sm text-gray-600">Configure global settings for provider management</p>
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

	{#if config}
		<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
			<!-- Fallback Strategy -->
			<div>
				<label for="fallback_strategy" class="block text-sm font-medium text-gray-700 mb-2">
					Fallback Strategy
				</label>
				<select
					id="fallback_strategy"
					bind:value={config.fallback_strategy}
					class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
					{#each fallbackStrategies as strategy}
						<option value={strategy}>{strategy}</option>
					{/each}
				</select>
				<p class="mt-1 text-xs text-gray-500">
					Strategy to use when primary provider fails: priority (by priority order), round_robin
					(rotate), random (random selection)
				</p>
			</div>

			<!-- Health Check Interval -->
			<div>
				<label for="health_check_interval" class="block text-sm font-medium text-gray-700 mb-2">
					Health Check Interval (seconds)
				</label>
				<input
					type="number"
					id="health_check_interval"
					bind:value={config.health_check_interval}
					min="0"
					class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
				<p class="mt-1 text-xs text-gray-500">
					How often to check provider health (0 to disable)
				</p>
			</div>

			<!-- Circuit Breaker -->
			<div class="border-t border-gray-200 pt-6">
				<h3 class="text-lg font-semibold text-gray-900 mb-4">Circuit Breaker</h3>
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label
							for="failure_threshold"
							class="block text-sm font-medium text-gray-700 mb-2"
						>
							Failure Threshold
						</label>
						<input
							type="number"
							id="failure_threshold"
							bind:value={config.circuit_breaker.failure_threshold}
							min="1"
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<p class="mt-1 text-xs text-gray-500">
							Number of failures before opening circuit
						</p>
					</div>
					<div>
						<label
							for="recovery_timeout"
							class="block text-sm font-medium text-gray-700 mb-2"
						>
							Recovery Timeout (seconds)
						</label>
						<input
							type="number"
							id="recovery_timeout"
							bind:value={config.circuit_breaker.recovery_timeout}
							min="1"
							class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<p class="mt-1 text-xs text-gray-500">Seconds to wait before retrying</p>
					</div>
				</div>
			</div>

			<!-- Actions -->
			<div class="flex items-center justify-end gap-3 pt-6 border-t border-gray-200">
				<button
					onclick={() => goto('/')}
					class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
				>
					Cancel
				</button>
				<button
					onclick={handleSave}
					disabled={saving || loading}
					class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{saving ? 'Saving...' : 'Save Configuration'}
				</button>
			</div>
		</div>
	{:else if loading}
		<div class="text-center text-gray-500 py-12">Loading configuration...</div>
	{:else}
		<div class="text-center text-gray-500 py-12">Failed to load configuration</div>
	{/if}
</div>
