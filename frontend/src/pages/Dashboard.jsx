import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listEvents } from '../services/eventService';

// Lista PROVISÓRIA só para conferir os eventos criados; a listagem oficial é a US 3.1.
export default function Dashboard() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    listEvents().then(setEvents).catch(() => setEvents([]));
  }, []);

  return (
    <main style={{ padding: '2rem', maxWidth: 720, margin: '0 auto' }}>
      <h1 style={{ color: 'var(--red)' }}>Painel administrativo</h1>
      <Link to="/admin/eventos/novo" style={{ color: 'var(--red)', fontWeight: 600 }}>
        + Novo evento
      </Link>

      <h2>Eventos cadastrados ({events.length})</h2>
      {events.length === 0 ? (
        <p>Nenhum evento cadastrado.</p>
      ) : (
        <ul>
          {events.map((ev) => (
            <li key={ev.id}>
              <strong>{ev.titulo}</strong> — {ev.data} {ev.hora} · {ev.local} · {ev.tipo}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}