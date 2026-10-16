import { useEffect, useState } from 'react';
import EventCard from '../components/EventCard';
import { getEvents, sortByDate } from '../services/eventService';
import '../styles/home.css';

export default function Home() {
  const [state, setState] = useState({ status: 'loading', events: [] });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let active = true;
    getEvents()
      .then((events) => active && setState({ status: 'success', events: sortByDate(events) }))
      .catch(() => active && setState({ status: 'error', events: [] }));
    return () => {
      active = false;
    };
  }, [attempt]);

  function retry() {
    setState({ status: 'loading', events: [] });
    setAttempt((a) => a + 1);
  }

  const { status, events } = state;

  return (
    <main className="home">
      <header className="home-hero">
        <h1>
          O que está <span>acontecendo</span> no CIn.
        </h1>
        <p>Palestras, workshops e hackathons em ordem cronológica.</p>
      </header>

      {status === 'loading' && <p role="status">Carregando eventos...</p>}

      {status === 'error' && (
        <div role="alert" className="home-error">
          <p>Não foi possível carregar os eventos.</p>
          <button type="button" onClick={retry}>Tentar novamente</button>
        </div>
      )}

      {status === 'success' && events.length === 0 && (
        <p className="home-empty">Nenhum evento disponível</p>
      )}

      {status === 'success' && events.length > 0 && (
        <section className="event-grid" aria-label="Lista de eventos">
          {events.map((event, i) => (
            <EventCard key={event.id} event={event} index={i} />
          ))}
        </section>
      )}
    </main>
  );
}