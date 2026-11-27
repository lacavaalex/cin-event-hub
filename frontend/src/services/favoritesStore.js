import { getAnonymousUserId } from './anonymousUser.js';

function storageKey() {
  return `cin_event_hub_favorites:${getAnonymousUserId()}`;
}

export function getFavoriteIds() {
  try {
    const raw = localStorage.getItem(storageKey());
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return [...new Set(parsed.map((id) => Number(id)).filter((id) => Number.isFinite(id)))];
  } catch {
    return [];
  }
}

function saveFavoriteIds(ids) {
  try {
    localStorage.setItem(storageKey(), JSON.stringify(ids));
  } catch {
    // Armazenamento indisponível no navegador.
  }
}

export function isEventFavorited(eventId) {
  return getFavoriteIds().includes(Number(eventId));
}

export function addFavoriteId(eventId) {
  const numericId = Number(eventId);
  const current = getFavoriteIds();
  if (!current.includes(numericId)) {
    saveFavoriteIds([...current, numericId]);
  }
  return true;
}

export function removeFavoriteId(eventId) {
  const numericId = Number(eventId);
  const next = getFavoriteIds().filter((id) => id !== numericId);
  saveFavoriteIds(next);
  return false;
}
