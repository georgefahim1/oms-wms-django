// frontend-web/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path' // <-- IMPORT PATH MODULE

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Add path resolution for absolute imports
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Alias @ to the src directory
    },
  },
})