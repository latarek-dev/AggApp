# --- STAGE 1: Build SPA ---
FROM node:20-alpine AS builder
WORKDIR /app

# zainstaluj zależności
COPY package*.json ./
RUN npm ci

# skopiuj źródła i zbuduj
COPY . .
# WPROWADŹ do buildu publiczną bazę API; doymślnie /api (bo za chwilę zaproxujemy to w Nginx)
ARG VITE_API_PUBLIC_BASE=/api
ENV REACT_APP_API_PUBLIC_BASE=${VITE_API_PUBLIC_BASE}
RUN npm run build

# --- STAGE 2: serwowanie przez Nginx ---
FROM nginx:alpine
# nasza konfiguracja serwera
COPY nginx.conf /etc/nginx/conf.d/default.conf
# statyki SPA do katalogu publicznego Nginx
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK CMD wget -q0- https://localhost >/dev/null || exit 1