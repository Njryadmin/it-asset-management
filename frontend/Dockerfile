# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Install perl for template processing
RUN apk add --no-cache perl

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx template and entrypoint script
COPY docker/nginx.conf /etc/nginx/nginx.conf.template
COPY docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
