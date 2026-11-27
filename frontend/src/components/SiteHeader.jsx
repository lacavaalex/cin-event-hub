import { NavLink } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { curatorLinkFor } from '../services/siteNavigation';
import ThemeToggle from './ThemeToggle';

const linkClass = ({ isActive }) => `site-nav-link${isActive ? ' active' : ''}`;

export default function SiteHeader() {
  const { token } = useAuth();
  const curator = curatorLinkFor(token);

  return (
    <header className="site-header">
      <div className="site-header-inner">
        <NavLink to="/" end className="site-brand">
          <img
            src="/logo-hub.png"
            alt=""
            className="site-brand-logo logo-light"
          />
          <img
            src="/logo-hub-dark.png"
            alt=""
            className="site-brand-logo logo-dark"
          />
          <span>Hub de Eventos</span>
        </NavLink>
        <div className="site-actions">
          <nav className="site-nav" aria-label="Navegação principal">
            <NavLink to="/" end className={linkClass}>
              Eventos
            </NavLink>
            <NavLink to="/favorites" className={linkClass}>
              Meus Favoritos
            </NavLink>
            <NavLink to={curator.to} className={linkClass}>
              {curator.label}
            </NavLink>
          </nav>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}