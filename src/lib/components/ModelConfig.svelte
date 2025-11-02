<script lang="ts">
	import type { ProviderModelConfig } from '$lib/types/config';

	let { models, onUpdate } = $props<{
		models: ProviderModelConfig;
		onUpdate: (models: ProviderModelConfig) => void;
	}>();

	let editingType = $state<'big' | 'middle' | 'small' | null>(null);
	let newModel = $state('');

	function addModel(type: 'big' | 'middle' | 'small') {
		if (!newModel.trim()) return;

		const updated = { ...models };
		if (!updated[type].includes(newModel.trim())) {
			updated[type] = [...updated[type], newModel.trim()];
			onUpdate(updated);
		}
		newModel = '';
		editingType = null;
	}

	function removeModel(type: 'big' | 'middle' | 'small', index: number) {
		const updated = { ...models };
		updated[type] = updated[type].filter((_: string, i: number) => i !== index);
		onUpdate(updated);
	}

	function moveModel(type: 'big' | 'middle' | 'small', index: number, direction: 'up' | 'down') {
		const updated = { ...models };
		const modelsList = [...updated[type]];
		const newIndex = direction === 'up' ? index - 1 : index + 1;

		if (newIndex < 0 || newIndex >= modelsList.length) return;

		[modelsList[index], modelsList[newIndex]] = [modelsList[newIndex], modelsList[index]];
		updated[type] = modelsList;
		onUpdate(updated);
	}
</script>

<div class="space-y-4">
	{#each ['big', 'middle', 'small'] as type}
		{@const modelType = type as 'big' | 'middle' | 'small'}
		{@const modelList = models[modelType]}
		<div class="border border-gray-200 rounded-lg p-4">
			<div class="flex items-center justify-between mb-3">
				<h4 class="text-sm font-semibold text-gray-700 capitalize">{type} Models</h4>
				<button
					type="button"
					onclick={() => (editingType = editingType === modelType ? null : modelType)}
					class="px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-700"
				>
					+ Add Model
				</button>
			</div>

			{#if editingType === modelType}
				<div class="flex gap-2 mb-3">
					<input
						type="text"
						bind:value={newModel}
						placeholder="Enter model name"
						class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						onkeydown={(e) => {
							if (e.key === 'Enter') {
								e.preventDefault();
								addModel(modelType);
							}
							if (e.key === 'Escape') {
								editingType = null;
								newModel = '';
							}
						}}
					/>
					<button
						type="button"
						onclick={() => addModel(modelType)}
						class="px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
					>
						Add
					</button>
					<button
						type="button"
						onclick={() => {
							editingType = null;
							newModel = '';
						}}
						class="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
					>
						Cancel
					</button>
				</div>
			{/if}

			{#if modelList.length === 0}
				<p class="text-sm text-gray-500 italic">No models configured</p>
			{:else}
				<ul class="space-y-1">
					{#each modelList as model, index}
						<li
							class="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-md hover:bg-gray-100"
						>
							<span class="text-sm text-gray-700 font-mono">{model}</span>
							<div class="flex items-center gap-1">
								<button
									type="button"
									onclick={() => moveModel(modelType, index, 'up')}
									disabled={index === 0}
									class="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
									title="Move up"
								>
									↑
								</button>
								<button
									type="button"
									onclick={() => moveModel(modelType, index, 'down')}
									disabled={index === modelList.length - 1}
									class="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
									title="Move down"
								>
									↓
								</button>
								<button
									type="button"
									onclick={() => removeModel(modelType, index)}
									class="p-1 text-red-400 hover:text-red-600"
									title="Remove"
									disabled={modelList.length === 1 && modelType === 'big'}
								>
									×
								</button>
							</div>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/each}
</div>
