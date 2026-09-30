import { TOKEN_KEY } from './authService';

// ATENÇÃO: MOCK TEMPORÁRIO.
// O backend e o banco de dados ainda não existem. Com VITE_USE_MOCK=true, os eventos
// ficam apenas no localStorage deste navegador (não são compartilhados nem definitivos).
// Na integração, use VITE_USE_MOCK=false: as funções abaixo já chamam a API
// (POST /events e GET /events) e as telas não precisam mudar.
const API_URL = import.meta.env.VITE_API_URL;
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const STORAGE_KEY = 'mock_events';

export const EVENT_TYPES = ['Palestra', 'Workshop', 'Hackathon'];

function authHeaders() {
  return { Authorization: `Bearer ${localStorage.getItem(TOKEN_KEY)}` };
}

function readMock() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) ?? [];
  } catch {
    return [];
  }
}

export async function listEvents() {
  if (USE_MOCK) return readMock();

  const res = await fetch(`${API_URL}/events`, { headers: authHeaders() });
  if (!res.ok) throw new Error('Não foi possível carregar os eventos.');
  return res.json();
}

export async function createEvent(data) {
  if (USE_MOCK) {
    const event = { id: crypto.randomUUID(), ...data };
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...readMock(), event]));
    return event;
  }

  let res;
  try {
    res = await fetch(`${API_URL}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify(data),
    });
  } catch {
    throw new Error('Erro de conexão. Tente novamente.');
  }
  if (!res.ok) throw new Error('Não foi possível criar o evento.');
  return res.json();
}