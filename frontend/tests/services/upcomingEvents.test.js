import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  addDays,
  formatDayLabel,
  selectUpcomingEvents,
  todayInRecife,
  UPCOMING_WINDOW_DAYS,
} from '../../src/services/upcomingEvents.js';

const REFERENCE = '2026-11-19';

const events = [
  { id: 1, title: 'Palestra de IA', date: '2026-11-20', time: '19:00:00', type: 'Palestra' },
  { id: 2, title: 'Workshop de React', date: '2026-11-19', time: '09:00', type: 'Workshop' },
  { id: 3, title: 'Hackathon', date: '2026-11-25', time: '08:00', type: 'Hackathon' },
  { id: 4, title: 'Evento passado', date: '2026-11-18', time: '10:00', type: 'Palestra' },
  { id: 5, title: 'Longe da semana', date: '2026-11-26', time: '10:00', type: 'Outro' },
  { id: 6, title: 'Mesmo dia, mais cedo', date: '2026-11-19', time: '14:30:00', type: 'Minicurso' },
];

test('a janela padrão cobre hoje e os seis dias seguintes', () => {
  assert.equal(UPCOMING_WINDOW_DAYS, 7);
  assert.equal(addDays(REFERENCE, UPCOMING_WINDOW_DAYS - 1), '2026-11-25');
});

test('selectUpcomingEvents filtra por janela e ordena por data e hora', () => {
  const selected = selectUpcomingEvents(events, REFERENCE);
  assert.deepEqual(
    selected.map((event) => event.id),
    [2, 6, 1, 3]
  );
});

test('selectUpcomingEvents devolve lista vazia quando não há eventos próximos', () => {
  assert.deepEqual(selectUpcomingEvents([events[3]], REFERENCE), []);
  assert.deepEqual(selectUpcomingEvents([], REFERENCE), []);
});

test('todayInRecife converte UTC para o fuso do Recife', () => {
  assert.equal(todayInRecife(new Date('2026-11-20T02:30:00Z')), '2026-11-19');
  assert.equal(todayInRecife(new Date('2026-11-19T12:00:00Z')), '2026-11-19');
});

test('formatDayLabel mostra dia e mês sem depender do fuso local', () => {
  const label = formatDayLabel('2026-11-20');
  assert.match(label, /20/);
  assert.match(label, /11/);
});
