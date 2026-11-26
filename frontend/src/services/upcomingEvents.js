export const UPCOMING_WINDOW_DAYS = 7;

const RECIFE = 'America/Recife';

export function todayInRecife(now = new Date()) {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: RECIFE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(now);
}

export function addDays(isoDate, days) {
  const base = new Date(`${isoDate}T12:00:00Z`);
  base.setUTCDate(base.getUTCDate() + days);
  return base.toISOString().slice(0, 10);
}

function sortKey(event) {
  return `${event.date}T${String(event.time ?? '').slice(0, 5)}`;
}

export function formatDayLabel(isoDate) {
  return new Intl.DateTimeFormat('pt-BR', {
    timeZone: 'UTC',
    weekday: 'short',
    day: '2-digit',
    month: '2-digit',
  }).format(new Date(`${isoDate}T12:00:00Z`));
}

export function selectUpcomingEvents(
  events,
  referenceDate = todayInRecife(),
  days = UPCOMING_WINDOW_DAYS
) {
  const start = referenceDate;
  const end = addDays(start, days - 1);
  return events
    .filter((event) => event.date >= start && event.date <= end)
    .sort((a, b) => sortKey(a).localeCompare(sortKey(b)));
}
