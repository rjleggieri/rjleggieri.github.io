import { defineConfig } from 'vite';
import { resolve } from 'node:path';
export default defineConfig({ build: { rollupOptions: { input: {
  main: resolve(import.meta.dirname, 'index.html'),
  nli: resolve(import.meta.dirname, 'projects/nli.html'),
  bqe: resolve(import.meta.dirname, 'projects/bqe.html'),
  evaluation: resolve(import.meta.dirname, 'projects/evaluation.html'),
  praxicom: resolve(import.meta.dirname, 'projects/praxicom.html'),
  prosody: resolve(import.meta.dirname, 'projects/text-prosody.html'),
  coursework: resolve(import.meta.dirname, 'projects/coursework.html')
} } } });
