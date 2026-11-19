export function curatorLinkFor(token) {
  return token
    ? { label: 'Painel', to: '/admin/events' }
    : { label: 'Área do curador', to: '/login' };
}
