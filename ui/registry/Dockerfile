# Build stage
FROM node:22-slim AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

FROM base AS builder

WORKDIR /app

# Copy lock file for dependency installation
COPY pnpm-lock.yaml .

# Fetch all dependencies (needed for build)
RUN pnpm fetch

# Copy source code
COPY . .

# Install dependencies
RUN pnpm install --frozen-lockfile

RUN pnpm run build

EXPOSE 4321

CMD ["pnpm", "preview", "--host"]
