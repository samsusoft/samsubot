# Use a lightweight web server image
FROM nginx:alpine

# Copy your public files into the Nginx public directory
COPY public/ /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

