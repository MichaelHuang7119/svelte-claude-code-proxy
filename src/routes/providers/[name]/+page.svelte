<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import type { ProviderConfig } from '$lib/types/config';
	import { configStore } from '$lib/stores/config';
	import ProviderForm from '$lib/components/ProviderForm.svelte';
	import { get } from 'svelte/store';

	let provider = $state<ProviderConfig | null>(null);
	let loading = $state(true);
	let storeLoading = $state(false);

	// Subscribe to loading store
	$effect(() => {
		const unsubscribe = configStore.loading.subscribe((value) => {
			storeLoading = value;
		});
		return unsubscribe;
	});

	$effect(() => {
		const providerName = $page.params.name ? decodeURIComponent($page.params.name) : '';
		if (!providerName) {
			loading = false;
			return;
		}
		const found = configStore.getProvider(providerName);
		
		if (found) {
			provider = { ...found };
		} else if (!storeLoading) {
			// Provider not found, redirect
			goto('/');
		}
		
		loading = false;
	});

	async function handleSubmit(submittedProvider: ProviderConfig) {
		const providerName = $page.params.name ? decodeURIComponent($page.params.name) : '';
		if (!providerName) return;
		configStore.updateProvider(providerName, submittedProvider);
		const success = await configStore.save();

		if (success) {
			goto('/');
		} else {
			const errorValue = get(configStore.error);
			alert(errorValue || 'Failed to save provider');
		}
	}

	function handleCancel() {
		if (confirm('Are you sure you want to cancel? Unsaved changes will be lost.')) {
			goto('/');
		}
	}

	function handleDelete() {
		const providerName = $page.params.name ? decodeURIComponent($page.params.name) : '';
		if (!providerName) return;
		
		const currentConfig = get(configStore.config);
		if (currentConfig && currentConfig.providers.length === 1) {
			alert('Cannot delete the last provider. At least one provider is required.');
			return;
		}

		if (confirm(`Are you sure you want to delete provider "${providerName}"? This action cannot be undone.`)) {
			configStore.removeProvider(providerName);
			configStore.save().then((success) => {
				if (success) {
					goto('/');
				} else {
					const errorValue = get(configStore.error);
					alert(errorValue || 'Failed to delete provider');
				}
			});
		}
	}
</script>

{#if loading}
	<div class="container mx-auto px-4 py-8">
		<div class="text-center text-gray-500">Loading provider...</div>
	</div>
{:else if provider}
	<div class="container mx-auto px-4 py-8 max-w-4xl">
		<div class="mb-6 flex items-center justify-between">
			<div>
				<h1 class="text-3xl font-bold text-gray-900">Edit Provider</h1>
				<p class="mt-2 text-sm text-gray-600">{provider.name}</p>
			</div>
			<button
				onclick={handleDelete}
				class="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 rounded-md hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500"
			>
				Delete Provider
			</button>
		</div>

		<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
			<ProviderForm {provider} onSubmit={handleSubmit} onCancel={handleCancel} />
		</div>
	</div>
{:else}
	<div class="container mx-auto px-4 py-8">
		<div class="text-center">
			<p class="text-gray-500 mb-4">Provider not found</p>
			<a href="/" class="text-blue-600 hover:text-blue-700">Go back to home</a>
		</div>
	</div>
{/if}
