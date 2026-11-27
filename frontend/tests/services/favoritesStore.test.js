import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';
import {
  addFavoriteId,
  getFavoriteIds,
  isEventFavorited,
  removeFavoriteId,
} from '../../src/services/favoritesStore.js';

function createMemoryStorage() {
  const data = new Map();
  return {
    getItem: (key) => (data.has(key) ? data.get(key) : null),
    setItem: (key, value) => data.set(key, String(value)),
    removeItem: (key) => data.delete(key),
    clear: () => data.clear(),
  };
}

beforeEach(() => {
  globalThis.localStorage = createMemoryStorage();
});

test('adiciona, consulta e remove favoritos sem duplicar IDs', () => {
  assert.deepEqual(getFavoriteIds(), []);
  assert.equal(isEventFavorited(10), false);

  addFavoriteId(10);
  addFavoriteId('10');
  addFavoriteId(25);

  assert.deepEqual(getFavoriteIds(), [10, 25]);
  assert.equal(isEventFavorited(10), true);
  assert.equal(isEventFavorited('25'), true);

  removeFavoriteId(10);
  assert.deepEqual(getFavoriteIds(), [25]);
  assert.equal(isEventFavorited(10), false);
});
