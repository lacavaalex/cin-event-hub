import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config.js';

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      setupFiles: './tests/setup.js',
      include: ['tests/**/*.test.{js,jsx}'],
      // os testes sempre usam o mock, independente do .env de cada pessoa
      env: { VITE_USE_MOCK: 'true' },
    },
  })
);