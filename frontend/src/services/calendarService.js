// Convenções assumidas (o backlog não define horário de término nem fuso):
const UTC_OFFSET_HOURS = 3; // America/Recife (UTC-3, sem horário de verão)
const DURATION_MINUTES = 60; // duração padrão, pois o evento só tem hora de início

// Formata como "20261020T220000Z"
function toIcsUtc(date) {
  return date.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
}

// Escapa caracteres especiais de campos de texto do iCalendar
function escapeText(value) {
  return String(value ?? '')
    .replace(/\\/g, '\\\\')
    .replace(/;/g, '\\;')
    .replace(/,/g, '\\,')
    .replace(/\r?\n/g, '\\n');
}

// Linhas do .ics têm no máximo 75 bytes; as maiores continuam na linha seguinte iniciada por espaço
function fold(line) {
  const encoder = new TextEncoder();
  let out = '';
  let current = '';
  let size = 0;
  let limit = 75;
  for (const ch of line) {
    const bytes = encoder.encode(ch).length;
    if (size + bytes > limit) {
      out += `${current}\r\n `;
      current = '';
      size = 0;
      limit = 74;
    }
    current += ch;
    size += bytes;
  }
  return out + current;
}

function fileName(title) {
  const slug = String(title ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return `${slug || 'evento'}.ics`;
}

function parseStart(date, time) {
  const [year, month, day] = String(date).slice(0, 10).split('-').map(Number);
  const [hour, minute] = String(time).split(':').map(Number);
  return new Date(Date.UTC(year, month - 1, day, hour + UTC_OFFSET_HOURS, minute));
}

// Usa o fim informado pelo evento; se não houver (ou for inválido), aplica a duração padrão
function resolveEnd(event, start) {
  const endDate = event.endDate ?? event.end_date ?? event.date;
  const endTime = event.endTime ?? event.end_time;
  if (endTime) {
    const end = parseStart(endDate, endTime);
    if (end > start) return end;
  }
  return new Date(start.getTime() + DURATION_MINUTES * 60000);
}

export function buildIcs(event, { url } = {}) {
  const start = parseStart(event.date, event.time);
  const end = resolveEnd(event, start);

  const description = [event.description, url ? `Inscrição: ${url}` : '']
    .filter(Boolean)
    .join('\n\n');

  const lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//CIn Event Hub//PT-BR//',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'BEGIN:VEVENT',
    `UID:event-${event.id}@cin-event-hub`,
    `DTSTAMP:${toIcsUtc(new Date())}`,
    `DTSTART:${toIcsUtc(start)}`,
    `DTEND:${toIcsUtc(end)}`,
    `SUMMARY:${escapeText(event.title)}`,
    `LOCATION:${escapeText(event.location)}`,
  ];
  if (description) lines.push(`DESCRIPTION:${escapeText(description)}`);
  if (url) lines.push(`URL:${url}`);
  lines.push('END:VEVENT', 'END:VCALENDAR');

  return `${lines.map(fold).join('\r\n')}\r\n`;
}

export function downloadIcs(event, options) {
  const blob = new Blob([buildIcs(event, options)], { type: 'text/calendar;charset=utf-8' });
  const href = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = href;
  link.download = fileName(event.title);
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(href), 0);
}