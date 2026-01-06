import * as React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore, useHasRole } from '@/store/authStore';
import { ROUTES, ROLE_LABELS, ROLES } from '@/lib/constants';
import { Button, Badge } from '@/components/ui';
import { LogOut } from 'lucide-react';

export function Navbar() {
  const { user, logout, isAuthenticated } = useAuthStore();
  const navigate = useNavigate();
  const isBorrower = useHasRole(ROLES.BORROWER);
  const isCollections = useHasRole(ROLES.ADMIN, ROLES.COLLECTIONS);

  const handleLogout = async () => {
    await logout();
    navigate(ROUTES.LOGIN);
  };

  if (!isAuthenticated || !user) return null;

  const homeRoute = isBorrower ? ROUTES.MY_LOANS : ROUTES.DASHBOARD;

  return (
    <nav className="sticky top-0 z-50 bg-primary text-white h-[60px]">
      <div className="max-w-7xl mx-auto px-5 h-full flex items-center justify-between">
        {/* Brand */}
        <Link
          to={homeRoute}
          className="flex items-center gap-3 text-white no-underline"
        >
          <img
            src="/logo.png"
            alt="Ancla Capital"
            className="h-10 w-auto"
          />
          <span className="font-semibold text-lg">Ancla Capital</span>
        </Link>

        {/* Navigation Links */}
        <ul className="flex items-center gap-1 list-none m-0 p-0">
          {!isBorrower ? (
            <>
              <NavLink to={ROUTES.DASHBOARD}>Dashboard</NavLink>
              <NavLink to={ROUTES.BORROWERS}>Prestatarios</NavLink>
              <NavLink to={ROUTES.PROPERTIES}>Propiedades</NavLink>
              <NavLink to={ROUTES.LOANS}>Préstamos</NavLink>
              <NavLink to={ROUTES.PAYMENTS}>Pagos</NavLink>
              {isCollections && (
                <NavLink to={ROUTES.COLLECTIONS}>Cobros</NavLink>
              )}
            </>
          ) : (
            <NavLink to={ROUTES.MY_LOANS}>Mis Préstamos</NavLink>
          )}
        </ul>

        {/* User Info */}
        <div className="flex items-center gap-3">
          <span className="text-sm">{user.fullName}</span>
          <Badge variant="info" size="sm">
            {ROLE_LABELS[user.role] || user.role}
          </Badge>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-white hover:bg-primary-light"
            leftIcon={<LogOut className="h-4 w-4" />}
          >
            Salir
          </Button>
        </div>
      </div>
    </nav>
  );
}

interface NavLinkProps {
  to: string;
  children: React.ReactNode;
}

function NavLink({ to, children }: NavLinkProps) {
  return (
    <li>
      <Link
        to={to}
        className="px-4 py-2 rounded text-white no-underline transition-colors hover:bg-primary-light"
      >
        {children}
      </Link>
    </li>
  );
}

export default Navbar;
