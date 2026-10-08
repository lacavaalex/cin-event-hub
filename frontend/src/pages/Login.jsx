import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import '../styles/login.css';

export default function Login() {
  const { token, login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [formError, setFormError] = useState('');
  const [loading, setLoading] = useState(false);

  // login ok => token salvo => redireciona para o painel
  if (token) return <Navigate to="/admin" replace />;

  async function handleSubmit(e) {
    e.preventDefault();
    const next = {};
    if (!email.trim()) next.email = 'Informe o e-mail institucional';
    if (!password) next.password = 'Informe a senha';
    setErrors(next);
    setFormError('');
    if (Object.keys(next).length) return;

    setLoading(true);
    try {
      await login(email.trim(), password);
    } catch (err) {
      setFormError(err.message);
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={handleSubmit} noValidate>
        <h1>Hub de Eventos</h1>
        <p>Acesse o painel administrativo</p>

        {formError && <div className="form-error" role="alert">{formError}</div>}

        <div className="field">
          <label htmlFor="email">E-mail institucional</label>
          <input id="email" type="email" value={email}
            className={errors.email ? 'invalid' : ''}
            onChange={(e) => setEmail(e.target.value)} />
          {errors.email && <span className="field-error">{errors.email}</span>}
        </div>

        <div className="field">
          <label htmlFor="password">Senha</label>
          <input id="password" type="password" value={password}
            className={errors.password ? 'invalid' : ''}
            onChange={(e) => setPassword(e.target.value)} />
          {errors.password && <span className="field-error">{errors.password}</span>}
        </div>

        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
    </main>
  );
}