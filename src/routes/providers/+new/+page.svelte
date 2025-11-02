<script lang="ts">
	import { goto } from '$app/navigation';
	import type { ProviderConfig } from '$lib/types/config';
	import { configStore } from '$lib/stores/config';
	import ProviderForm from '$lib/components/ProviderForm.svelte';
	import { get } from 'svelte/store';

	let config = $state<ReturnType<typeof configStore.config> | null>(null);
	let error = $state<string | null>(null);

	// Subscribe to config store
	$effect(() => {
		const unsubscribe = configStore.config.subscribe((value) => {
			config = value;
		});
		return unsubscribe;
	});

	// Subscribe to error store
	$effect(() => {
		const unsubscribe = configStore.error.subscribe((value) => {
			error = value;
		});
		return unsubscribe;
	});

	// Initialize default provider with reactive config
	const defaultProvider = $derived.by((): ProviderConfig => {
		return {
			name: '',
			enabled: true,
			priority: config?.providers.length
				? Math.max(...config.providers.map((p) => p.priority)) + 1
				: 1,
			api_key: '',
			base_url: '',
			api_version: null,
			timeout: 90,
			max_retries: 3,
			custom_headers: {},
			models: {
				big: [],
				middle: [],
				small: []
			}
		};
	});

	let provider = $state<ProviderConfig>({ ...defaultProvider });
	
	// Update provider when defaultProvider changes
	$effect(() => {
		provider = { ...defaultProvider };
	});

	async function handleSubmit(submittedProvider: ProviderConfig) {
		configStore.addProvider(submittedProvider);
		const success = await configStore.save();

		if (success) {
			goto('/');
		} else {
			alert(error || 'Failed to save provider');
		}
	}

	function handleCancel() {
		if (confirm('Are you sure you want to cancel? Unsaved changes will be lost.')) {
			goto('/');
		}
	}
</script>

<div class="container mx-auto px-4 py-8 max-w-4xl">
	<div class="mb-6">
		<h1 class="text-3xl font-bold text-gray-900">Add New Provider</h1>
		<p class="mt-2 text-sm text-gray-600">Configure a new LLM provider</p>
	</div>

	<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
		<ProviderForm {provider} onSubmit={handleSubmit} onCancel={handleCancel} />
	</div>
</div>
