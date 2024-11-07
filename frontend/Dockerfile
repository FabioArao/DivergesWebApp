# Use Node.js 18 Alpine image
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec7bf9888a6aab3ec#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Create npm cache directory
RUN mkdir -p /home/node/.npm
ENV npm_config_cache=/home/node/.npm

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm config set cache /home/node/.npm && \
    npm ci --prefer-offline --no-audit

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /home/node/.npm /home/node/.npm
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED 1

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
# Disable telemetry during runtime
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built assets
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Set correct permissions
RUN mkdir -p /app/.next && chown nextjs:nodejs /app/.next

# Use non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set environment variables
ENV PORT 3000
ENV HOSTNAME localhost

# Start the application
CMD ["node", "server.js"]
