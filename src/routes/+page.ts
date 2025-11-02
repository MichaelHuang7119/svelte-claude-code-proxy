import type { PageLoad } from './$types';
import type { ProviderManagerConfig } from '$lib/types/config';
import { browser } from '$app/environment';

export const load: PageLoad = async ({ fetch, depends }) => {
	// Load config on page load
	depends('config:providers');
	
	// Only load on client side to avoid SSR issues with backend connection
	// Server-side can't access localhost:8082 through Vite proxy
	if (!browser) {
		// Return empty data for SSR, let client-side load it
		return {
			config: undefined
		};
	}
	
	try {
		// Use relative URL (via Vite proxy) in browser
		const url = '/api/config/providers';
		
		const response = await fetch(url);
		
		if (!response.ok) {
			return {
				error: `Failed to load config: ${response.status} ${response.statusText}`
			};
		}
		
		const config: ProviderManagerConfig = await response.json();
		return {
			config
		};
	} catch (error) {
		console.error('Failed to load config in page load:', error);
		return {
			error: error instanceof Error ? error.message : 'Failed to load configuration'
		};
	}
};