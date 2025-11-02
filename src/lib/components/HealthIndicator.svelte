<script lang="ts">
	import type { ProviderStatus } from '$lib/types/config';

	let { status } = $props<{ status: ProviderStatus }>();

	const statusColors: Record<ProviderStatus, string> = {
		healthy: 'bg-green-100 text-green-800 border-green-300',
		unhealthy: 'bg-yellow-100 text-yellow-800 border-yellow-300',
		circuit_open: 'bg-red-100 text-red-800 border-red-300'
	};

	const statusIcons: Record<ProviderStatus, string> = {
		healthy: '✓',
		unhealthy: '⚠',
		circuit_open: '✗'
	};

	const statusLabels: Record<ProviderStatus, string> = {
		healthy: 'Healthy',
		unhealthy: 'Unhealthy',
		circuit_open: 'Circuit Open'
	};
</script>

<div
	class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border {statusColors[status as ProviderStatus]}"
>
	<span>{statusIcons[status as ProviderStatus]}</span>
	<span>{statusLabels[status as ProviderStatus]}</span>
</div>
