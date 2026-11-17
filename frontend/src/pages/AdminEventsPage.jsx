import { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import DeleteEventButton from '../components/events/DeleteEventButton';
import { getAdminEvents } from '../services/eventsApi';
import '../styles/admin.css';

function formatDate(iso) {
  const [year, month, day] = iso.split('-');
  return `${day}/${month}/${year}`;
}

function statusOf(event) {
  if (event.is_expired) {
    return { label: 'Encerrado', className: 'admin-status admin-status--expired' };
  }
  if (event.status === 'active') {
    return { label: 'Ativo', className: 'admin-status admin-status--active' };
  }
  return { label: 'Inativo', className: 'admin-status admin-status--inactive' };
}

export default function AdminEventsPage() {
  const [state, setState] = useState({ status: 'loading', events: [] });
  const [attempt, setAttempt] = useState(0);
  const location = useLocation();
  const navigate = useNavigate();
  const [flash, setFlash] = useState(location.state?.flash ?? '');

  useEffect(() => {
    const controller = new AbortController();

    getAdminEvents(controller.signal)
      .then((events) => setState({ status: 'success', events }))
      .catch((error) => {
        if (error.name === 'AbortError') return;
        setState({ status: 'error', events: [] });
      });

    return () => controller.abort();
  }, [attempt]);

  useEffect(() => {
    if (location.state?.flash) {
      navigate('.', { replace: true, state: null });
    }
  }, [location.state, navigate]);

  function retry() {
    setState({ status: 'loading', events: [] });
    setAttempt((value) => value + 1);
  }

  function handleDeleted(event) {
    setState((previous) => ({
      ...previous,
      events: previous.events.filter((item) => item.id !== event.id),
    }));
    setFlash(`Evento "${event.title}" excluído com sucesso.`);
  }

  const { status, events } = state;
  const countText = `${events.length} ${events.length === 1 ? 'evento cadastrado' : 'eventos cadastrados'}`;

  return (
    <section className="admin-page">
      <header className="admin-page-header">
        <div>
          <h1 className="admin-title">Eventos</h1>
          {status === 'success' && (
            <p className="admin-subtitle" aria-live="polite">{countText}</p>
          )}
        </div>
        <Link to="/admin/events/new" className="admin-primary-button">
          Novo Evento
        </Link>
      </header>

      {flash && <p role="status" className="admin-flash">{flash}</p>}

      {status === 'loading' && <p role="status" className="admin-loading">Carregando eventos...</p>}

      {status === 'error' && (
        <div role="alert" className="admin-error">
          <p>Não foi possível carregar os eventos.</p>
          <button type="button" className="admin-secondary-button" onClick={retry}>
            Tentar novamente
          </button>
        </div>
      )}

      {status === 'success' && events.length === 0 && (
        <div className="admin-empty">
          <p>Nenhum evento cadastrado</p>
          <Link to="/admin/events/new" className="admin-primary-button">
            Novo Evento
          </Link>
        </div>
      )}

      {status === 'success' && events.length > 0 && (
        <div className="admin-table-wrapper">
          <table className="admin-table" aria-label="Eventos cadastrados">
            <thead>
              <tr>
                <th scope="col">Título</th>
                <th scope="col">Tipo</th>
                <th scope="col">Data e hora</th>
                <th scope="col">Local</th>
                <th scope="col">Status</th>
                <th scope="col">Ações</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => {
                const statusInfo = statusOf(event);
                return (
                  <tr key={event.id}>
                    <td><strong>{event.title}</strong></td>
                    <td>{event.event_type}</td>
                    <td>
                      <time dateTime={event.date}>{formatDate(event.date)}</time>
                      <span className="admin-time">{event.time.slice(0, 5)}</span>
                    </td>
                    <td>{event.location}</td>
                    <td>
                      <span className={statusInfo.className}>{statusInfo.label}</span>
                    </td>
                    <td>
                      <div className="admin-row-actions">
                        <Link
                          to={`/admin/events/${event.id}/edit`}
                          className="admin-secondary-button"
                          aria-label={`Editar evento ${event.title}`}
                        >
                          Editar
                        </Link>
                        <DeleteEventButton event={event} onDeleted={handleDeleted} />
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
