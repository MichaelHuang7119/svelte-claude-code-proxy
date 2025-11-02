import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			// Claude API endpoints for client access
			'/v1': {
				target: 'http://localhost:8082',
				changeOrigin: true
			},
			// Frontend management API
			'/api': {
				target: 'http://localhost:8082',
				changeOrigin: true
			},
			'/health': {
				target: 'http://localhost:8082',
				changeOrigin: true
			},
			'/test-connection': {
				target: 'http://localhost:8082',
				changeOrigin: true
			}
		}
	}
});
