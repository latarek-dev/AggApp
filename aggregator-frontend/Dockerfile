FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
ARG VITE_API_PUBLIC_BASE=/api
ENV REACT_APP_API_PUBLIC_BASE=${VITE_API_PUBLIC_BASE}
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK CMD wget -q0- https://localhost >/dev/null || exit 1