# Stage 1: Build the app
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies
COPY package*.json ./ 
COPY vite.config.ts ./
COPY postcss.config.js ./

RUN npm install
# TypeScript types for React
RUN npm install --save-dev @types/react @types/react-dom


COPY . .
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]