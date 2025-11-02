import type { Handle } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

// Server-side proxy for API requests
export const handle: Handle = async ({ event, resolve }) => {
	// Proxy API requests to backend
	if (event.url.pathname.startsWith('/api/') || 
	    event.url.pathname.startsWith('/v1/') || 
	    event.url.pathname === '/health' || 
	    event.url.pathname === '/test-connection') {
		
		// Use environment variable or default to Docker internal address
		const backendUrl = env.VITE_API_BASE_URL || 'http://backend:8082';
		
		// Forward request to backend
		const url = `${backendUrl}${event.url.pathname}${event.url.search}`;
		
		try {
			const response = await fetch(url, {
				method: event.request.method,
				headers: {
					'Content-Type': 'application/json',
					...(event.request.headers.get('authorization') && {
						'Authorization': event.request.headers.get('authorization')!
					})
				},
				body: event.request.method !== 'GET' && event.request.method !== 'HEAD' 
					? await event.request.text() 
					: undefined
			});
			
			const data = await response.text();
			
			return new Response(data, {
				status: response.status,
				statusText: response.statusText,
				headers: {
					'Content-Type': response.headers.get('Content-Type') || 'application/json',
					'Access-Control-Allow-Origin': '*',
					'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
					'Access-Control-Allow-Headers': 'Content-Type, Authorization'
				}
			});
		} catch (error) {
			console.error('[Server Proxy] Error proxying request:', error);
			return new Response(
				JSON.stringify({ error: 'Failed to proxy request to backend', details: String(error) }),
				{
					status: 500,
					headers: { 'Content-Type': 'application/json' }
				}
			);
		}
	}
	
	return resolve(event);
};

