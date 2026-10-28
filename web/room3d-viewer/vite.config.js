import { defineConfig } from 'vite';

// base relativa: lo stesso build funziona servito alla radice o sotto un
// sottopercorso qualsiasi (es. /salamai/room3d/), senza ricompilare.
export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
    chunkSizeWarningLimit: 1200,
  },
  server: { host: '127.0.0.1', port: 5173 },
});
