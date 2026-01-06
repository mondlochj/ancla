import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, Phone, Mail } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { DataTable, Currency } from '@/components/data';
import { Card, Button, Spinner, Badge } from '@/components/ui';
import { paymentsService } from '@/services';
import { formatDate, formatCurrency } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import type { PaymentSchedule } from '@/types';

export default function OverduePayments() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['overdue-payments'],
    queryFn: () => paymentsService.getOverduePayments(),
  });

  const getDaysOverdue = (dueDate: string) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diff = Math.floor((today.getTime() - due.getTime()) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const getSeverity = (days: number) => {
    if (days <= 15) return 'warning';
    if (days <= 30) return 'error';
    return 'critical';
  };

  const columns = [
    {
      key: 'loan',
      header: 'Préstamo',
      render: (payment: PaymentSchedule) => (
        <div>
          <Link to={ROUTES.LOAN_DETAIL(payment.loanId)} className="text-blue-600 hover:underline font-medium">
            {payment.loanNumber}
          </Link>
          <div className="text-sm text-gray-500">
            {payment.borrowerName}
          </div>
        </div>
      ),
    },
    {
      key: 'amount',
      header: 'Monto Pendiente',
      render: (payment: PaymentSchedule) => (
        <Currency amount={payment.amount} className="font-semibold" />
      ),
    },
    {
      key: 'dueDate',
      header: 'Fecha de Vencimiento',
      render: (payment: PaymentSchedule) => (
        <div>
          <div>{formatDate(payment.dueDate)}</div>
          <div className="text-sm text-gray-500">
            Cuota #{payment.paymentNumber}
          </div>
        </div>
      ),
    },
    {
      key: 'daysOverdue',
      header: 'Días de Atraso',
      render: (payment: PaymentSchedule) => {
        const days = getDaysOverdue(payment.dueDate);
        const severity = getSeverity(days);
        return (
          <Badge
            variant={severity === 'critical' ? 'danger' : severity === 'error' ? 'warning' : 'default'}
          >
            {days} días
          </Badge>
        );
      },
    },
    {
      key: 'contact',
      header: 'Contacto',
      render: (payment: PaymentSchedule) => (
        <div className="flex items-center gap-2">
          {payment.borrowerPhone && (
            <a href={`tel:${payment.borrowerPhone}`} className="p-2 hover:bg-gray-100 rounded-full">
              <Phone className="h-4 w-4 text-gray-500" />
            </a>
          )}
          {payment.borrowerEmail && (
            <a href={`mailto:${payment.borrowerEmail}`} className="p-2 hover:bg-gray-100 rounded-full">
              <Mail className="h-4 w-4 text-gray-500" />
            </a>
          )}
        </div>
      ),
    },
    {
      key: 'actions',
      header: 'Acciones',
      render: (payment: PaymentSchedule) => (
        <div className="flex items-center gap-2">
          <Link to={`${ROUTES.PAYMENT_NEW}?loanId=${payment.loanId}`}>
            <Button size="sm">
              Registrar Pago
            </Button>
          </Link>
          <Link to={ROUTES.COLLECTION_NEW(payment.loanId)}>
            <Button variant="outline" size="sm">
              Gestión de Cobro
            </Button>
          </Link>
        </div>
      ),
    },
  ];

  if (error) {
    return (
      <PageLayout>
        <div className="text-center text-red-600">Error al cargar pagos vencidos</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="mb-6">
        <Link to={ROUTES.PAYMENTS} className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a pagos
        </Link>
      </div>

      <PageHeader
        title="Pagos Vencidos"
        description="Préstamos con pagos pendientes que requieren atención"
      />

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card>
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Vencido</p>
                    <p className="text-2xl font-bold text-red-600">
                      {formatCurrency(data?.data.reduce((sum, p) => sum + p.amount, 0) || 0)}
                    </p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-red-500" />
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Cuotas Vencidas</p>
                    <p className="text-2xl font-bold">{data?.total || 0}</p>
                  </div>
                </div>
              </div>
            </Card>
            <Card>
              <div className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Préstamos Afectados</p>
                    <p className="text-2xl font-bold">
                      {new Set(data?.data.map(p => p.loanId)).size || 0}
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {!data?.data.length ? (
            <Card>
              <div className="p-12 text-center">
                <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <AlertTriangle className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">Sin pagos vencidos</h3>
                <p className="text-gray-500 mt-2">Todos los préstamos están al día</p>
              </div>
            </Card>
          ) : (
            <DataTable columns={columns} data={data.data} keyExtractor={(p) => `${p.loanId}-${p.paymentNumber}`} />
          )}
        </>
      )}
    </PageLayout>
  );
}
