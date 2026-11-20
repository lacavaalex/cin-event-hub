import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { getAnonymousUserId } from '../services/anonymousUser';

export default function FavoritesPage() {
  const anonymousId = useMemo(() => getAnonymousUserId(), []);

  return (
    <main className="favorites-page" data-anonymous-user-id={anonymousId}>
      <h1>Meus Favoritos</h1>
      <p className="favorites-lead">
        Seus favoritos são associados a este navegador, sem login de aluno.
      </p>
      <p className="favorites-empty">Você ainda não tem eventos favoritos</p>
      <p className="favorites-id">
        Identificador anônimo: <code>{anonymousId.slice(0, 8)}…</code>
      </p>
      <Link to="/" className="favorites-back">Ver eventos</Link>
    </main>
  );
}
