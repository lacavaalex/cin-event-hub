import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
  formatDayLabel,
  selectUpcomingEvents,
  UPCOMING_WINDOW_DAYS,
} from '../services/upcomingEvents';

const KNOWN_TYPES = ['palestra', 'workshop', 'hackathon', 'minicurso'];

function typeSlug(type) {
  const slug = String(type ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();
  return KNOWN_TYPES.includes(slug) ? slug : 'outros';
}

export default function UpcomingEvents({ events, referenceDate, days = UPCOMING_WINDOW_DAYS }) {
  const upcoming = useMemo(
    () => selectUpcomingEvents(events, referenceDate, days),
    [events, referenceDate, days]
  );

  if (upcoming.length === 0) return null;

  return (
    <section className="upcoming" aria-labelledby="upcoming-title">
      <h2 id="upcoming-title">Esta semana</h2>
      <ol className="upcoming-list">
        {upcoming.map((event) => {
          const type = event.event_type ?? event.type;
          return (
            <li key={event.id} className={`upcoming-item type-${typeSlug(type)}`}>
              <Link to={`/eventos/${event.id}`} className="upcoming-link">
                <time className="upcoming-day" dateTime={event.date}>
                  {formatDayLabel(event.date)}
                </time>
                <span className="upcoming-title">{event.title}</span>
                <span className="upcoming-time">{String(event.time ?? '').slice(0, 5)}</span>
                <span className="upcoming-type">{type}</span>
                <span className="sr-only">Ver detalhes</span>
              </Link>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
