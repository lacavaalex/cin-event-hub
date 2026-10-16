import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getEventById } from '../services/eventService';
import '../styles/details.css';

const MONTHS = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
const DESC_LIMIT = 280;

function formatDate(iso) {
  const [year, month, day] = iso.split('-');
  return `${Number(day)} de ${MONTHS[Number(month) - 1]} de ${year}`;
}

// Só aceita http/https: evita links "javascript:" vindos de dados externos
function safeUrl(value) {
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

function Description({ text }) {
  const [expanded, setExpanded] = useState(false);
  const isLong = text.length > DESC_LIMIT;
  const shown = !isLong || expanded ? text : `${text.slice(0, DESC_LIMIT).trimEnd()}…`;

  return (
    <div>
      <p className="details-desc" id="event-desc">{shown}</p>
      {isLong && (
        <button
          type="button"
          className="details-toggle"
          aria-expanded={expanded}
          aria-controls="event-desc"
          onClick={() => setExpanded((v) => !v)}
        >
          {expanded ? 'Mostrar menos' : 'Ler mais'}
        </button>
      )}
    </div>
  );
}

export default function EventDetails() {
  const { id } = useParams();
  const [state, setState] = useState({ id: null, status: 'loading', event: null });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    getEventById(id)
      .then((event) => active && setState({ id, status: 'success', event }))
      .catch((err) =>
        active &&
        setState({ id, status: err.message === 'NOT_FOUND' ? 'notfound' : 'error', event: null })
      );
    return () => {
      active = false;
    };
  }, [id, attempt]);

  function retry() {
    setState({ id: null, status: 'loading', event: null });
    setAttempt((a) => a + 1);
  }

  const { status, event } = state.id === id ? state : { status: 'loading', event: null };
  const link = event ? safeUrl(event.registration_link) : null;

  return (
    <main className="details">
      <Link to="/" className="details-back">← Voltar</Link>

      {status === 'loading' && <p role="status">Carregando evento...</p>}

      {status === 'notfound' && <p className="details-empty">Evento não encontrado</p>}

      {status === 'error' && (
        <div role="alert" className="details-error">
          <p>Não foi possível carregar o evento.</p>
          <button type="button" onClick={retry}>Tentar novamente</button>
        </div>
      )}

      {status === 'success' && (
        <article className="details-grid">
          <div>
            <span className="details-type">{event.type}</span>
            <h1 className="details-title">{event.title}</h1>
            <Description key={event.id} text={event.description || 'Sem descrição informada.'} />
          </div>

          <aside className="details-side" aria-label="Informações do evento">
            <dl>
              <dt>Data</dt>
              <dd><time dateTime={event.date}>{formatDate(event.date)}</time></dd>
              <dt>Hora</dt>
              <dd>{event.time.slice(0, 5)}</dd>
              <dt>Local</dt>
              <dd>{event.location}</dd>
              <dt>Tipo</dt>
              <dd>{event.type}</dd>
            </dl>
            {link ? (
              <a className="details-cta" href={link} target="_blank" rel="noopener noreferrer">
                Inscrever-se
              </a>
            ) : (
              <p className="details-nolink">Link de inscrição não informado</p>
            )}
          </aside>
        </article>
      )}
    </main>
  );
}