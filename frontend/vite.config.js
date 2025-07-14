import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // Frontend development server will run on port 3000
    proxy: {
      // Proxy API requests to the backend server
      '/api': {
        target: 'http://127.0.0.1:5000', // The address of the Python backend
        changeOrigin: true, // Necessary for virtual-hosted sites
        secure: false, // Don't verify SSL certificate
      },
    },
  },
  build: {
    outDir: 'build', // Specify the output directory for the build
  },
})
