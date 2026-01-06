import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Eye, AlertTriangle } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { DataTable, StatusBadge, EmptyState, Pagination, Currency } from '@/components/data';
import { Button, Input, Select, Card, Spinner } from '@/components/ui';
import { paymentsService } from '@/services';
import { formatDate } from '@/lib/utils';
import { PAYMENT_STATUS_OPTIONS, ROUTES } from '@/lib/constants';
import type { Payment, PaymentFilters } from '@/types';

export default function PaymentList() {
  const [filters, setFilters] = useState<PaymentFilters>({
    page: 1,
    pageSize: 10,
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['payments', filters],
    queryFn: () => paymentsService.getPayments(filters),
  });

  const columns = [
    {
      key: 'loan',
      header: 'Préstamo',
      render: (payment: Payment) => (
        <Link to={ROUTES.LOAN_DETAIL(payment.loanId)} className="text-blue-600 hover:underline font-medium">
          {payment.loanNumber || payment.loanId}
        </Link>
      ),
    },
    {
      key: 'amount',
      header: 'Monto',
      render: (payment: Payment) => <Currency amount={payment.amount} />,
    },
    {
      key: 'type',
      header: 'Tipo',
      render: (payment: Payment) => (
        <span className="capitalize">{payment.paymentType}</span>
      ),
    },
    {
      key: 'dueDate',
      header: 'Fecha de Vencimiento',
      render: (payment: Payment) => formatDate(payment.dueDate),
    },
    {
      key: 'paymentDate',
      header: 'Fecha de Pago',
      render: (payment: Payment) => payment.paymentDate ? formatDate(payment.paymentDate) : '-',
    },
    {
      key: 'status',
      header: 'Estado',
      render: (payment: Payment) => (
        <StatusBadge status={payment.status} type="payment" />
      ),
    },
    {
      key: 'actions',
      header: 'Acciones',
      render: (payment: Payment) => (
        <div className="flex items-center gap-2">
          <Link to={ROUTES.PAYMENT_DETAIL(payment.id)}>
            <Button variant="ghost" size="sm">
              <Eye className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      ),
    },
  ];

  if (error) {
    return (
      <PageLayout>
        <div className="text-center text-red-600">Error al cargar pagos</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Pagos"
        description="Historial y gestión de pagos"
        action={
          <div className="flex gap-2">
            <Link to={ROUTES.PAYMENTS_OVERDUE}>
              <Button variant="outline" className="text-amber-600 border-amber-600">
                <AlertTriangle className="h-4 w-4 mr-2" />
                Ver Vencidos
              </Button>
            </Link>
            <Link to={ROUTES.PAYMENT_NEW}>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Registrar Pago
              </Button>
            </Link>
          </div>
        }
      />

      <Card className="mb-6">
        <div className="p-4 flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar por número de préstamo..."
                className="pl-10"
                value={filters.search || ''}
                onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
              />
            </div>
          </div>
          <Select
            value={filters.status || ''}
            onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
            options={[
              { value: '', label: 'Todos los estados' },
              ...PAYMENT_STATUS_OPTIONS,
            ]}
          />
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Más filtros
          </Button>
        </div>
      </Card>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : !data?.data.length ? (
        <EmptyState
          title="No hay pagos"
          description="Los pagos aparecerán aquí cuando se registren"
        />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} keyExtractor={(p) => p.id} />
          <div className="mt-4">
            <Pagination
              currentPage={filters.page || 1}
              totalPages={data.totalPages}
              onPageChange={(page) => setFilters({ ...filters, page })}
            />
          </div>
        </>
      )}
    </PageLayout>
  );
}
