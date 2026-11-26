import { Link, NavLink, Outlet } from 'react-router-dom';
import LogoutButton from './LogoutButton';
import ThemeToggle from './ThemeToggle';
import '../styles/admin-layout.css';

const navClassName = ({ isActive }) =>
  `admin-nav-link${isActive ? ' active' : ''}`;

export default function AdminLayout() {
  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div>
          <p className="admin-brand-kicker">Hub de Eventos</p>
          <p className="admin-brand-title">Painel administrativo</p>
        </div>

        <nav aria-label="Navegação do painel administrativo">
          <ul className="admin-nav">
            <li>
              <NavLink to="/admin/events" className={navClassName}>
                Eventos
              </NavLink>
            </li>
            <li>
              <NavLink to="/admin/extraction" className={navClassName}>
                Status de Extração
              </NavLink>
            </li>
            <li>
              <Link to="/" className="admin-nav-link">
                Ver site
              </Link>
            </li>
            <li>
              <LogoutButton className="admin-nav-link admin-nav-button" />
            </li>
          </ul>
        </nav>
        <ThemeToggle />
      </aside>

      <main className="admin-content">
        <Outlet />
      </main>
    </div>
  );
}
