import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import EventCard from '../components/EventCard';
import FavoriteButton from '../components/events/FavoriteButton';
import { getAnonymousUserId } from '../services/anonymousUser';
import { getEvents, sortByDate } from '../services/eventService';
import { getFavoriteIds } from '../services/favoritesStore';
import '../styles/home.css';

export default function FavoritesPage() {
  const anonymousId = useMemo(() => getAnonymousUserId(), []);
  const [favoriteIds, setFavoriteIds] = useState(() => getFavoriteIds());
  const [state, setState] = useState({ status: 'loading', events: [] });

  useEffect(() => {
    let active = true;
    getEvents({ pageSize: 100 })
      .then((events) => active && setState({ status: 'success', events: sortByDate(events) }))
      .catch(() => active && setState({ status: 'error', events: [] }));
    return () => {
      active = false;
    };
  }, []);

  const favoriteEvents = useMemo(
    () => state.events.filter((event) => favoriteIds.includes(Number(event.id))),
    [state.events, favoriteIds]
  );

  function handleToggle(eventId, isNowFavorited) {
    setFavoriteIds((prev) =>
      isNowFavorited ? [...new Set([...prev, Number(eventId)])] : prev.filter((id) => id !== Number(eventId))
    );
  }

  return (
    <main className="favorites-page" data-anonymous-user-id={anonymousId}>
      <h1>Meus Favoritos</h1>
      <p className="favorites-lead">
        Seus favoritos são associados a este navegador, sem login de aluno.
      </p>

      {state.status === 'loading' && <p role="status">Carregando favoritos...</p>}

      {state.status === 'error' && (
        <p role="alert" className="favorites-empty">
          Não foi possível carregar os eventos favoritos no momento.
        </p>
      )}

      {state.status === 'success' && favoriteEvents.length === 0 && (
        <p className="favorites-empty">Você ainda não tem eventos favoritos</p>
      )}

      {state.status === 'success' && favoriteEvents.length > 0 && (
        <section className="favorites-list" aria-label="Eventos favoritados">
          {favoriteEvents.map((event, index) => (
            <div key={event.id} className="favorites-item">
              <EventCard event={event} index={index} />
              <div className="favorites-item-action">
                <FavoriteButton
                  eventId={event.id}
                  initialIsFavorited
                  onChange={(next) => handleToggle(event.id, next)}
                />
              </div>
            </div>
          ))}
        </section>
      )}

      <p className="favorites-id">
        Identificador anônimo: <code>{anonymousId.slice(0, 8)}…</code>
      </p>
      <Link to="/" className="favorites-back">Ver eventos</Link>
    </main>
  );
}
