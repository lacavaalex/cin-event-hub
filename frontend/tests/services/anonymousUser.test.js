import assert from 'node:assert/strict';
import { afterEach, beforeEach, test } from 'node:test';
import { ANONYMOUS_ID_KEY, getAnonymousUserId } from '../../src/services/anonymousUser.js';

const originalStorage = globalThis.localStorage;

beforeEach(() => {
  const store = new Map();
  globalThis.localStorage = {
    getItem: (key) => (store.has(key) ? store.get(key) : null),
    setItem: (key, value) => store.set(key, String(value)),
    removeItem: (key) => store.delete(key),
  };
});

afterEach(() => {
  globalThis.localStorage = originalStorage;
});

test('gera e persiste um identificador anônimo no navegador', () => {
  const id = getAnonymousUserId();
  assert.match(id, /^[0-9a-f-]{36}$/i);
  assert.equal(localStorage.getItem(ANONYMOUS_ID_KEY), id);
});

test('reaproveita o identificador anônimo nas visitas seguintes', () => {
  localStorage.setItem(ANONYMOUS_ID_KEY, 'id-existente');
  assert.equal(getAnonymousUserId(), 'id-existente');
});
