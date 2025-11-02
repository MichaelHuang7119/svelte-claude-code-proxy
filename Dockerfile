# Frontend Dockerfile for SvelteKit
FROM node:20-slim as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
# VITE_API_BASE_URL is set as build arg and env var for build time
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# Production stage
FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package.json ./

# Copy node_modules from build stage (includes adapter-node needed at runtime)
# This is more reliable than reinstalling, as adapter-node is in devDependencies
# but required at runtime by SvelteKit adapter-node
# Note: We copy all dependencies to ensure runtime compatibility
COPY --from=build /app/node_modules ./node_modules

# Copy built application from build stage
COPY --from=build /app/build ./build
COPY --from=build /app/static ./static

# Set environment to production
ENV NODE_ENV=production
ENV PORT=3000
ENV HOST=0.0.0.0

# Start the application using SvelteKit's built-in server
CMD ["node", "build/index.js"]

