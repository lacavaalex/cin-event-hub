import { useState } from "react";
import { favoriteEvent, unfavoriteEvent } from "../../services/eventsApi";
export default function FavoriteButton({ eventId, initialIsFavorited = false, onChange }) {
  const [isFavorited, setIsFavorited] = useState(initialIsFavorited);
  const [isSaving, setIsSaving] = useState(false);

  async function handleClick() {
    if (isSaving) return;

    const next = !isFavorited;
    setIsFavorited(next); // otimista: muda já, antes da API responder
    setIsSaving(true);

    try {
      if (next) {
        await favoriteEvent(eventId);
      } else {
        await unfavoriteEvent(eventId);
      }
      onChange?.(next);
    } catch {
      setIsFavorited(!next); // desfaz a mudança otimista em caso de erro
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
      aria-label={isFavorited ? "Remover dos favoritos" : "Adicionar aos favoritos"}
      className={`favorite-button${isFavorited ? ' is-favorited' : ''}`}
    >
      {isFavorited ? "★" : "☆"}
    </button>
  );
}