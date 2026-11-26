
const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

async function request(path) {
  const token = localStorage.getItem('token');

  const headers = {
    Accept: 'application/json'
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;

  try {
    response = await fetch(`${API_URL}${path}`, {
      method: 'GET',
      headers
    });
  } catch {
    throw new Error('Erro de conexão com o servidor. Tente novamente.');
  }

  if (response.status === 401 || response.status === 403) {
    throw new Error('Sessão expirada ou acesso não autorizado.');
  }

  if (!response.ok) {
    throw new Error(
      `Não foi possível consultar a extração (${response.status}).`
    );
  }

  return response.json();
}

export function getExtractionStatus() {
  return request('/extraction/status');
}

export function getExtractionAlerts() {
  return request('/extraction/alerts');
}
