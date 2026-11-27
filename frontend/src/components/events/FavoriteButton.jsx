import { useState } from 'react';
import { favoriteEvent, unfavoriteEvent } from '../../services/eventsApi';
import {
  addFavoriteId,
  isEventFavorited,
  removeFavoriteId,
} from '../../services/favoritesStore';

export default function FavoriteButton({
  eventId,
  initialIsFavorited,
  showLabel = false,
  onChange,
}) {
  const [isFavorited, setIsFavorited] = useState(
    () => initialIsFavorited ?? isEventFavorited(eventId)
  );
  const [isSaving, setIsSaving] = useState(false);

  async function handleClick() {
    if (isSaving) return;

    const next = !isFavorited;
    setIsFavorited(next);
    if (next) {
      addFavoriteId(eventId);
    } else {
      removeFavoriteId(eventId);
    }
    onChange?.(next);
    setIsSaving(true);

    try {
      // Sincronização best-effort com a API (mantém o favorito local salvo no navegador).
      if (next) {
        await favoriteEvent(eventId);
      } else {
        await unfavoriteEvent(eventId);
      }
    } catch {
      // A preferência anônima permanece persistida em localStorage.
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={isSaving}
      aria-pressed={isFavorited}
      aria-label={isFavorited ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
      className={`favorite-button${showLabel ? ' favorite-button--details' : ''}${
        isFavorited ? ' is-favorited' : ''
      }`}
    >
      <span aria-hidden="true">{isFavorited ? '★' : '☆'}</span>
      {showLabel && (
        <span>{isFavorited ? 'Salvo nos favoritos' : 'Favoritar evento'}</span>
      )}
    </button>
  );
}
