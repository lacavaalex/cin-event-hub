import { useEffect, useMemo, useRef, useState } from 'react';
import EventCard from '../components/EventCard';
import Pagination from '../components/Pagination';
import { filterByKeyword, getEvents, sortByDate } from '../services/eventService';
import '../styles/home.css';

const PAGE_SIZE = 20;

export default function Home() {
  const [state, setState] = useState({ status: 'loading', events: [] });
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const listRef = useRef(null);

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

  // Mudar a busca sempre volta para a página 1
  function handleSearch(value) {
    setQuery(value);
    setPage(1);
  }

  function goToPage(next) {
    setPage(next);
    listRef.current?.scrollIntoView({ block: 'start' });
  }

  const { status, events } = state;
  const visible = useMemo(() => filterByKeyword(events, query), [events, query]);
  const hasQuery = query.trim() !== '';

  const totalPages = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
  const currentPage = Math.min(page, totalPages);
  const start = (currentPage - 1) * PAGE_SIZE;
  const pageEvents = visible.slice(start, start + PAGE_SIZE);

  const countText =
    totalPages > 1
      ? `Exibindo ${start + 1}–${start + pageEvents.length} de ${visible.length} eventos`
      : `${visible.length} ${visible.length === 1 ? 'evento' : 'eventos'}`;

  return (
    <main className="home">
      <header className="home-hero">
        <h1>
          O que está <span>acontecendo</span> no CIn.
        </h1>
        <p>Palestras, workshops e hackathons em ordem cronológica.</p>
      </header>

      <div className="home-search" role="search">
        <label htmlFor="event-search" className="sr-only">
          Pesquisar eventos por palavra-chave
        </label>
        <input
          id="event-search"
          type="search"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Pesquisar por título ou descrição..."
          autoComplete="off"
        />
        {hasQuery && (
          <button type="button" className="home-search-clear" onClick={() => handleSearch('')}>
            Limpar busca
          </button>
        )}
      </div>

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
        <p className="home-count" aria-live="polite">{countText}</p>
      )}

      {status === 'success' && events.length > 0 && visible.length === 0 && (
        <p className="home-empty">Nenhum resultado encontrado</p>
      )}

      {status === 'success' && visible.length > 0 && (
        <>
          <section className="event-grid" aria-label="Lista de eventos" ref={listRef}>
            {pageEvents.map((event, i) => (
              <EventCard key={event.id} event={event} index={i} />
            ))}
          </section>
          <Pagination page={currentPage} totalPages={totalPages} onChange={goToPage} />
        </>
      )}
    </main>
  );
}