import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, CardHeader, CardBody, Button, Spinner } from '@/components/ui';
import { DataTable, Currency, StatusBadge } from '@/components/data';
import type { Column } from '@/components/data';
import { ROUTES } from '@/lib/constants';
import { formatDate, formatPercentage } from '@/lib/utils';
import type { Loan, DashboardMetrics } from '@/types';
import {
  TrendingUp,
  Wallet,
  AlertTriangle,
  PieChart,
  Plus,
} from 'lucide-react';

// Mock data - will be replaced with API calls
const mockMetrics: DashboardMetrics = {
  totalPortfolioValue: 2500000,
  activeLoansCount: 45,
  defaultRate: 0.033,
  averageLtv: 0.32,
  monthlyInterestIncome: 250000,
  overduePaymentsCount: 3,
  overdueAmount: 45000,
  loansByStatus: {
    Draft: 2,
    UnderReview: 5,
    Approved: 3,
    Active: 45,
    Matured: 12,
    Defaulted: 2,
    LegalReady: 1,
    Closed: 20,
  },
  loansByDepartment: {
    Guatemala: 25,
    Escuintla: 10,
    Sacatepéquez: 8,
    Quetzaltenango: 7,
  },
  recentLoans: [],
};

const mockRecentLoans: Loan[] = [
  {
    id: '1',
    loanNumber: 'AC-2401-A1B2',
    referenceNumber: 'AC-2401-A1B2',
    borrower: { id: '1', fullName: 'Juan Pérez' } as Loan['borrower'],
    property: { id: '1' } as Loan['property'],
    loanProduct: { id: '1', name: 'Estándar' } as Loan['loanProduct'],
    amount: 150000,
    termMonths: 12,
    interestRate: 0.10,
    ltv: 0.35,
    status: 'Active',
    startDate: '2024-01-15T10:00:00Z',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    loanNumber: 'AC-2401-C3D4',
    referenceNumber: 'AC-2401-C3D4',
    borrower: { id: '2', fullName: 'María García' } as Loan['borrower'],
    property: { id: '2' } as Loan['property'],
    loanProduct: { id: '1', name: 'Premium' } as Loan['loanProduct'],
    amount: 250000,
    termMonths: 24,
    interestRate: 0.08,
    ltv: 0.28,
    status: 'UnderReview',
    startDate: '2024-01-14T10:00:00Z',
    createdAt: '2024-01-14T10:00:00Z',
    updatedAt: '2024-01-14T10:00:00Z',
  },
];

export function Dashboard() {
  const navigate = useNavigate();
  const [isLoading] = React.useState(false);
  const metrics = mockMetrics;

  const loanColumns: Column<Loan>[] = [
    {
      key: 'referenceNumber',
      header: 'Referencia',
      render: (loan) => (
        <span className="font-medium text-secondary">{loan.referenceNumber}</span>
      ),
    },
    {
      key: 'borrower',
      header: 'Prestatario',
      render: (loan) => loan.borrower.fullName,
    },
    {
      key: 'amount',
      header: 'Monto',
      render: (loan) => <Currency amount={loan.amount} />,
    },
    {
      key: 'status',
      header: 'Estado',
      render: (loan) => <StatusBadge status={loan.status} type="loan" />,
    },
    {
      key: 'createdAt',
      header: 'Fecha',
      render: (loan) => formatDate(loan.createdAt),
    },
  ];

  if (isLoading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center py-20">
          <Spinner size="lg" />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Dashboard"
        subtitle="Resumen del portafolio de préstamos"
        actions={
          <Button
            leftIcon={<Plus className="h-4 w-4" />}
            onClick={() => navigate(ROUTES.LOAN_CREATE)}
          >
            Nuevo Préstamo
          </Button>
        }
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-6">
        <StatCard
          icon={<Wallet className="h-6 w-6 text-secondary" />}
          title="Valor del Portafolio"
          value={<Currency amount={metrics.totalPortfolioValue} />}
        />
        <StatCard
          icon={<TrendingUp className="h-6 w-6 text-success" />}
          title="Préstamos Activos"
          value={metrics.activeLoansCount}
        />
        <StatCard
          icon={<PieChart className="h-6 w-6 text-info" />}
          title="LTV Promedio"
          value={formatPercentage(metrics.averageLtv)}
        />
        <StatCard
          icon={<AlertTriangle className="h-6 w-6 text-danger" />}
          title="Tasa de Mora"
          value={formatPercentage(metrics.defaultRate)}
          variant={metrics.defaultRate > 0.05 ? 'danger' : 'default'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Loans */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader
              actions={
                <Button
                  variant="link"
                  onClick={() => navigate(ROUTES.LOANS)}
                >
                  Ver todos
                </Button>
              }
            >
              Préstamos Recientes
            </CardHeader>
            <CardBody className="p-0">
              <DataTable
                columns={loanColumns}
                data={mockRecentLoans}
                keyExtractor={(loan) => loan.id}
                onRowClick={(loan) => navigate(`/loans/${loan.id}`)}
              />
            </CardBody>
          </Card>
        </div>

        {/* Loans by Status */}
        <div>
          <Card>
            <CardHeader>Préstamos por Estado</CardHeader>
            <CardBody>
              <div className="space-y-3">
                {Object.entries(metrics.loansByStatus)
                  .filter(([_, count]) => count > 0)
                  .map(([status, count]) => (
                    <div
                      key={status}
                      className="flex items-center justify-between"
                    >
                      <StatusBadge status={status} type="loan" />
                      <span className="font-medium text-gray-700">{count}</span>
                    </div>
                  ))}
              </div>
            </CardBody>
          </Card>

          {/* Overdue Alert */}
          {metrics.overduePaymentsCount > 0 && (
            <Card className="mt-6 border-l-4 border-l-danger">
              <CardBody>
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-danger flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {metrics.overduePaymentsCount} Pagos Vencidos
                    </h4>
                    <p className="text-sm text-gray-500 mt-1">
                      Total: <Currency amount={metrics.overdueAmount} />
                    </p>
                    <Button
                      variant="link"
                      size="sm"
                      className="mt-2 p-0"
                      onClick={() => navigate('/payments/overdue')}
                    >
                      Ver detalles
                    </Button>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </PageLayout>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: React.ReactNode;
  change?: string;
  variant?: 'default' | 'success' | 'danger';
}

function StatCard({ icon, title, value, change, variant = 'default' }: StatCardProps) {
  return (
    <Card>
      <CardBody className="flex items-start gap-4">
        <div className="p-3 rounded-lg bg-gray-100">{icon}</div>
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            {title}
          </p>
          <p className="text-2xl font-semibold text-gray-900 mt-1">{value}</p>
          {change && (
            <p
              className={`text-xs mt-1 ${
                variant === 'success'
                  ? 'text-success'
                  : variant === 'danger'
                  ? 'text-danger'
                  : 'text-gray-500'
              }`}
            >
              {change}
            </p>
          )}
        </div>
      </CardBody>
    </Card>
  );
}

export default Dashboard;
