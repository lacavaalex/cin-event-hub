import { afterEach } from 'vitest';
import { randomUUID } from 'node:crypto';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// garantia para ambientes sem crypto.randomUUID (usado pelo eventService)
if (globalThis.crypto && !globalThis.crypto.randomUUID) {
  Object.defineProperty(globalThis.crypto, 'randomUUID', { value: randomUUID, configurable: true });
}

// cada teste começa limpo: sem DOM antigo e sem token/eventos no localStorage
afterEach(() => {
  cleanup();
  localStorage.clear();
});