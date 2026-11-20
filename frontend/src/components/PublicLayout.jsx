import { Outlet } from 'react-router-dom';
import SiteHeader from './SiteHeader';

export default function PublicLayout() {
  return (
    <div className="site-shell">
      <SiteHeader />
      <div className="site-content">
        <Outlet />
      </div>
    </div>
  );
}
