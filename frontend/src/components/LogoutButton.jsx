import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function LogoutButton({ className = '' }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  return (
    <button type="button" onClick={handleLogout} className={className || undefined}>
      Sair
    </button>
  );
}