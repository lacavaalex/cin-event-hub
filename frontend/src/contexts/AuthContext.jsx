import { createContext, useContext, useState } from 'react';
import * as authService from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(authService.TOKEN_KEY));

  async function login(email, password) {
    const { token } = await authService.login(email, password);
    localStorage.setItem(authService.TOKEN_KEY, token);
    setToken(token);
  }

  return <AuthContext.Provider value={{ token, login }}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);