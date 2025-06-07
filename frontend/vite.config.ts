import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/wikipitch/actions': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  },
  root: './src',
  base: '/wikipitch/',
  build: {
    outDir: '../../output/frontend',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        chunkFileNames: '[name].js',
        assetFileNames: '[name][extname]',
        entryFileNames: '[name].js',
      }
    }
  }
})