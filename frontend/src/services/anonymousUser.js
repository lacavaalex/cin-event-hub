export const ANONYMOUS_ID_KEY = 'anonymous_user_id';

export function getAnonymousUserId() {
  let id = localStorage.getItem(ANONYMOUS_ID_KEY);
  if (!id) {
    id = globalThis.crypto?.randomUUID?.()
      ?? `anon-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    localStorage.setItem(ANONYMOUS_ID_KEY, id);
  }
  return id;
}
