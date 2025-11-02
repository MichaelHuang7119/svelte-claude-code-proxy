<script lang="ts">
	import type { ProviderConfig, ProviderModelConfig } from '$lib/types/config';
	import ModelConfig from './ModelConfig.svelte';

	let { provider, onSubmit, onCancel } = $props<{
		provider: ProviderConfig;
		onSubmit: (provider: ProviderConfig) => void | Promise<void>;
		onCancel: () => void;
	}>();

	let formData = $state({ ...provider });
	let customHeadersEntries = $state<Array<{ key: string; value: string }>>(
		Object.entries(formData.custom_headers).map(([key, value]) => ({ key, value: String(value) }))
	);
	let showApiKey = $state(false);

	function updateModels(models: ProviderModelConfig) {
		formData.models = models;
	}

	function addCustomHeader() {
		customHeadersEntries = [...customHeadersEntries, { key: '', value: '' }];
	}

	function removeCustomHeader(index: number) {
		customHeadersEntries = customHeadersEntries.filter((_, i) => i !== index);
	}

	function updateCustomHeaders() {
		const headers: Record<string, string> = {};
		customHeadersEntries.forEach(({ key, value }: { key: string; value: string }) => {
			if (key.trim()) {
				headers[key.trim()] = value.trim();
			}
		});
		formData.custom_headers = headers;
	}

	async function handleSubmit() {
		updateCustomHeaders();
		await onSubmit(formData);
	}
</script>

<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-6">
	<div class="grid grid-cols-1 gap-6">
		<!-- Name -->
		<div>
			<label for="name" class="block text-sm font-medium text-gray-700 mb-1">
				Name <span class="text-red-500">*</span>
			</label>
			<input
				type="text"
				id="name"
				bind:value={formData.name}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				placeholder="e.g., openai, azure, ollama"
			/>
		</div>

		<!-- Enabled & Priority -->
		<div class="grid grid-cols-2 gap-4">
			<div>
				<label class="flex items-center gap-2">
					<input type="checkbox" bind:checked={formData.enabled} class="rounded" />
					<span class="text-sm font-medium text-gray-700">Enabled</span>
				</label>
			</div>
			<div>
				<label for="priority" class="block text-sm font-medium text-gray-700 mb-1">
					Priority <span class="text-red-500">*</span>
				</label>
				<input
					type="number"
					id="priority"
					bind:value={formData.priority}
					required
					min="1"
					class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
				<p class="mt-1 text-xs text-gray-500">Lower number = higher priority</p>
			</div>
		</div>

		<!-- API Key -->
		<div>
			<label for="api_key" class="block text-sm font-medium text-gray-700 mb-1">
				API Key <span class="text-red-500">*</span>
			</label>
			<div class="relative">
				<input
					type={showApiKey ? 'text' : 'password'}
					id="api_key"
					bind:value={formData.api_key}
					required
					class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
					placeholder={'${ENV_VAR_NAME}' + ' or actual key'}
				/>
				<button
					type="button"
					onclick={() => (showApiKey = !showApiKey)}
					class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
					tabindex="-1"
					aria-label={showApiKey ? 'Hide API key' : 'Show API key'}
				>
					{#if showApiKey}
						<!-- Eye off icon (hide) -->
						<svg
							class="w-5 h-5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
							></path>
						</svg>
					{:else}
						<!-- Eye icon (show) -->
						<svg
							class="w-5 h-5"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
							></path>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
							></path>
						</svg>
					{/if}
				</button>
			</div>
			<p class="mt-1 text-xs text-gray-500">Use {'${'}ENV_VAR{'}'} format for environment variables</p>
		</div>

		<!-- Base URL -->
		<div>
			<label for="base_url" class="block text-sm font-medium text-gray-700 mb-1">
				Base URL <span class="text-red-500">*</span>
			</label>
			<input
				type="url"
				id="base_url"
				bind:value={formData.base_url}
				required
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
				placeholder="https://api.example.com/v1"
			/>
		</div>

		<!-- API Version -->
		<div>
			<label for="api_version" class="block text-sm font-medium text-gray-700 mb-1">
				API Version (optional)
			</label>
			<input
				type="text"
				id="api_version"
				bind:value={formData.api_version}
				class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				placeholder="e.g., 2024-02-15-preview (for Azure)"
			/>
		</div>

		<!-- Timeout & Max Retries -->
		<div class="grid grid-cols-2 gap-4">
			<div>
				<label for="timeout" class="block text-sm font-medium text-gray-700 mb-1">
					Timeout (seconds)
				</label>
				<input
					type="number"
					id="timeout"
					bind:value={formData.timeout}
					min="1"
					class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
			</div>
			<div>
				<label for="max_retries" class="block text-sm font-medium text-gray-700 mb-1">
					Max Retries
				</label>
				<input
					type="number"
					id="max_retries"
					bind:value={formData.max_retries}
					min="0"
					class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
			</div>
		</div>

		<!-- Custom Headers -->
		<div>
			<div class="flex items-center justify-between mb-2">
				<span class="block text-sm font-medium text-gray-700">Custom Headers</span>
				<button
					type="button"
					onclick={addCustomHeader}
					class="text-xs text-blue-600 hover:text-blue-700"
				>
					+ Add Header
				</button>
			</div>
			<div class="space-y-2">
				{#each customHeadersEntries as entry, index}
					<div class="flex gap-2">
						<input
							type="text"
							bind:value={entry.key}
							placeholder="Header name"
							class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<input
							type="text"
							bind:value={entry.value}
							placeholder="Header value"
							class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
						<button
							type="button"
							onclick={() => removeCustomHeader(index)}
							class="px-3 py-2 text-red-600 hover:text-red-700"
						>
							×
						</button>
					</div>
				{/each}
				{#if customHeadersEntries.length === 0}
					<p class="text-sm text-gray-500 italic">No custom headers</p>
				{/if}
			</div>
		</div>

		<!-- Models Configuration -->
		<div>
			<span class="block text-sm font-medium text-gray-700 mb-2">Models Configuration</span>
			<ModelConfig models={formData.models} onUpdate={updateModels} />
		</div>
	</div>

	<!-- Form Actions -->
	<div class="flex items-center justify-end gap-3 pt-6 border-t border-gray-200">
		<button
			type="button"
			onclick={onCancel}
			class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
		>
			Cancel
		</button>
		<button
			type="submit"
			class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
		>
			Save Provider
		</button>
	</div>
</form>
