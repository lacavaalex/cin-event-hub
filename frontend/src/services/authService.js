const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
export const TOKEN_KEY = 'token';

export async function login(email, password) {
  let res;
  try {
    res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
  } catch {
    throw new Error('Erro de conexão. Tente novamente.');
  }

  if (!res.ok) {
    throw new Error('Credenciais inválidas');
  }

  return res.json();
}