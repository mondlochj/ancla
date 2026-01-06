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
import { LoanList, LoanDetail, LoanForm } from '@/pages/loans';
import { BorrowerList, BorrowerDetail, BorrowerForm } from '@/pages/borrowers';
import { PropertyList, PropertyDetail, PropertyForm } from '@/pages/properties';
import { PaymentList, PaymentRecord, OverduePayments } from '@/pages/payments';
import { CollectionList, CollectionForm } from '@/pages/collections';
import { DocumentList } from '@/pages/documents';

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

      {/* Protected Routes - Dashboard */}
      <Route
        path={ROUTES.DASHBOARD}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* Loans Routes */}
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
      <Route
        path="/loans/:id"
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <LoanDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/loans/:id/edit"
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.CREDIT_OFFICER]}>
            <LoanForm />
          </ProtectedRoute>
        }
      />

      {/* Borrowers Routes */}
      <Route
        path={ROUTES.BORROWERS}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <BorrowerList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/borrowers/new"
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.CREDIT_OFFICER]}>
            <BorrowerForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/borrowers/:id"
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <BorrowerDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/borrowers/:id/edit"
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.CREDIT_OFFICER]}>
            <BorrowerForm />
          </ProtectedRoute>
        }
      />

      {/* Properties Routes */}
      <Route
        path={ROUTES.PROPERTIES}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <PropertyList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/properties/new"
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.CREDIT_OFFICER]}>
            <PropertyForm />
          </ProtectedRoute>
        }
      />
      <Route
        path="/properties/:id"
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <PropertyDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/properties/:id/edit"
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.CREDIT_OFFICER]}>
            <PropertyForm />
          </ProtectedRoute>
        }
      />

      {/* Payments Routes */}
      <Route
        path={ROUTES.PAYMENTS}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <PaymentList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/payments/new"
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.CREDIT_OFFICER, ROLES.COLLECTIONS]}>
            <PaymentRecord />
          </ProtectedRoute>
        }
      />
      <Route
        path="/payments/overdue"
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <OverduePayments />
          </ProtectedRoute>
        }
      />

      {/* Collections Routes */}
      <Route
        path={ROUTES.COLLECTIONS}
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.COLLECTIONS]}>
            <CollectionList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/collections/new/:loanId"
        element={
          <ProtectedRoute roles={[ROLES.ADMIN, ROLES.COLLECTIONS]}>
            <CollectionForm />
          </ProtectedRoute>
        }
      />

      {/* Documents Routes */}
      <Route
        path={ROUTES.DOCUMENTS}
        element={
          <ProtectedRoute roles={INTERNAL_ROLES}>
            <DocumentList />
          </ProtectedRoute>
        }
      />

      {/* Borrower Portal */}
      <Route
        path={ROUTES.MY_LOANS}
        element={
          <ProtectedRoute roles={[ROLES.BORROWER]}>
            <BorrowerPortal />
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

// Borrower Portal - simplified view for borrowers
function BorrowerPortal() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-4xl mx-auto py-8 px-4">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">Mis Préstamos</h1>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500">Portal del prestatario en desarrollo.</p>
        </div>
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
