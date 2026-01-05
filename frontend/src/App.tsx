import * as React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from '@/store/authStore';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ROUTES, ROLES } from '@/lib/constants';
import { Spinner } from '@/components/ui';

// Pages
import { Login, Register } from '@/pages/auth';
import { Dashboard } from '@/pages/dashboard';
import { LoanList, LoanForm } from '@/pages/loans';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

// Internal roles (non-borrower)
const INTERNAL_ROLES = [ROLES.ADMIN, ROLES.CREDIT_OFFICER, ROLES.LEGAL, ROLES.COLLECTIONS];

function AppRoutes() {
  const { isAuthenticated, isLoading, refreshUser } = useAuthStore();

  React.useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path={ROUTES.LOGIN}
        element={
          isAuthenticated ? <Navigate to={ROUTES.DASHBOARD} replace /> : <Login />
        }
      />
      <Route
        path={ROUTES.REGISTER}
        element={
          isAuthenticated ? <Navigate to={ROUTES.DASHBOARD} replace /> : <Register />
        }
      />

      {/* Protected Routes - Internal Users */}
      <Route
        path={ROUTES.DASHBOARD}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.LOANS}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <LoanList />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.LOAN_CREATE}
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.CREDIT_OFFICER]}>
            <LoanForm />
          </ProtectedRoute>
        }
      />

      {/* Placeholder routes for future pages */}
      <Route
        path={ROUTES.BORROWERS}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <PlaceholderPage title="Prestatarios" />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.PROPERTIES}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <PlaceholderPage title="Propiedades" />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.PAYMENTS}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <PlaceholderPage title="Pagos" />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.COLLECTIONS}
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.COLLECTIONS]}>
            <PlaceholderPage title="Cobros" />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.DOCUMENTS}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <PlaceholderPage title="Documentos" />
          </ProtectedRoute>
        }
      />

      {/* Borrower Portal */}
      <Route
        path={ROUTES.MY_LOANS}
        element={
          <ProtectedRoute roles={[ROLES.BORROWER]}>
            <PlaceholderPage title="Mis Préstamos" />
          </ProtectedRoute>
        }
      />

      {/* Default redirect */}
      <Route
        path={ROUTES.HOME}
        element={<Navigate to={ROUTES.DASHBOARD} replace />}
      />

      {/* 404 */}
      <Route
        path="*"
        element={<NotFoundPage />}
      />
    </Routes>
  );
}

// Placeholder component for pages not yet implemented
function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">{title}</h1>
        <p className="text-gray-500">Esta página está en desarrollo.</p>
      </div>
    </div>
  );
}

// 404 Page
function NotFoundPage() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Página no encontrada</h2>
        <p className="text-gray-500 mb-6">La página que busca no existe.</p>
        <a href={ROUTES.DASHBOARD} className="text-secondary hover:underline">
          Volver al inicio
        </a>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
