import assert from 'node:assert/strict';
import { test } from 'node:test';
import { curatorLinkFor } from '../../src/services/siteNavigation.js';

test('visitante sem token vê Área do curador e vai para o login', () => {
  assert.deepEqual(curatorLinkFor(null), {
    label: 'Área do curador',
    to: '/login',
  });
});

test('curador autenticado vê Painel e vai para o painel', () => {
  assert.deepEqual(curatorLinkFor('token'), {
    label: 'Painel',
    to: '/admin/events',
  });
});
