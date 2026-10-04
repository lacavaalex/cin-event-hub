const API_URL = import.meta.env.VITE_API_URL;
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
export const TOKEN_KEY = 'token';

async function mockLogin(email, password) {
  await new Promise((r) => setTimeout(r, 400));
  if (email === 'admin@cin.ufpe.br' && password === '123456') {
    return { token: `mock.${btoa(JSON.stringify({ email }))}.sig` };
  }
  throw new Error('Credenciais inválidas');
}

export async function login(email, password) {
  if (USE_MOCK) return mockLogin(email, password);

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
  if (!res.ok) throw new Error('Credenciais inválidas');
  return res.json(); // esperado: { token: "<jwt>" }
}