import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // Load environment variables based on the current mode (development, production, etc.)
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [react()],
    
    // 👇 Use correct base path for Docker/Nginx builds
    base: './',

    // 👇 Build output settings
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },

    // 👇 Development server proxy
    server: {
      proxy: {
        '/auth': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
        },
        '/chat': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true,
        },
      },
    },

    // 👇 Optional: make aliases if needed (e.g., @ for src/)
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
  };
});
