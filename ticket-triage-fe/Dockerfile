# ── Stage 1: Development ──────────────────────────────────
FROM node:20-alpine AS dev

# Kích hoạt pnpm qua Corepack
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install

COPY . .

EXPOSE 5173
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]

# ── Stage 2: Production Build ─────────────────────────────
FROM dev AS build
RUN pnpm run build

# ── Stage 3: Demo Nginx ───────────────────────────────────
FROM nginx:alpine AS demo
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
