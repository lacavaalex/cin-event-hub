const MONTHS = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'];
const KNOWN_TYPES = ['palestra', 'workshop', 'hackathon', 'minicurso'];
import { Link } from 'react-router-dom';


function typeSlug(type) {
  const slug = type.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  return KNOWN_TYPES.includes(slug) ? slug : 'outros';
}

export default function EventCard({ event, index = 0 }) {
  const [year, month, day] = event.date.split('-');

  return (
    <article className={`event-card type-${typeSlug(event.type)}`} style={{ '--i': index }}>
      <time className="event-date" dateTime={event.date}>
        <span className="event-day">{day}</span>
        <span className="event-month">{MONTHS[Number(month) - 1]}</span>
        <span className="event-year">{year}</span>
      </time>
      <div className="event-body">
        <span className="event-type">{event.type}</span>
            <Link to={`/eventos/${event.id}`}>{event.title}</Link>
        <h3 className="event-title">{event.title}</h3>
        <p className="event-meta">{event.time.slice(0, 5)}</p>
        <p className="event-meta">{event.location}</p>
      </div>
    </article>
  );
}