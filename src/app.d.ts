// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { ProviderManagerConfig } from '$lib/types/config';

declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		interface PageData {
			config?: ProviderManagerConfig;
			error?: string;
		}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
