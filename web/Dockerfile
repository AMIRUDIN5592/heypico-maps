# Simple static frontend using Nginx
FROM nginx:1.27-alpine

# Copy static assets
COPY ./public /usr/share/nginx/html

# Default Nginx serves index.html at /
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
