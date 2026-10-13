import { useState } from 'react';
import * as authService from '../services/authService';
import { AuthContext } from './authContextValue';

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(authService.TOKEN_KEY));

  async function login(email, password) {
    const { token } = await authService.login(email, password);
    localStorage.setItem(authService.TOKEN_KEY, token);
    setToken(token);
  }

  function logout() {
    localStorage.removeItem(authService.TOKEN_KEY);
    setToken(null);
  }

  return <AuthContext.Provider value={{ token, login, logout }}>{children}</AuthContext.Provider>;
}