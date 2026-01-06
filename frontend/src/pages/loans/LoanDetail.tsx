import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Edit, FileText, DollarSign, AlertTriangle } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, Button, Spinner } from '@/components/ui';
import { StatusBadge, Currency, DataTable } from '@/components/data';
import { loansService, paymentsService } from '@/services';
import { formatDate, formatCurrency, calculateLtv } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import { useAuthStore } from '@/store/authStore';
import type { PaymentSchedule } from '@/types';

export default function LoanDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuthStore();

  const { data: loan, isLoading } = useQuery({
    queryKey: ['loan', id],
    queryFn: () => loansService.getLoan(id!),
    enabled: !!id,
  });

  const { data: scheduleData } = useQuery({
    queryKey: ['loan-schedule', id],
    queryFn: () => paymentsService.getLoanSchedule(id!),
    enabled: !!id,
  });

  const scheduleColumns = [
    {
      key: 'paymentNumber',
      header: '#',
      render: (item: PaymentSchedule) => item.paymentNumber,
    },
    {
      key: 'dueDate',
      header: 'Fecha de Vencimiento',
      render: (item: PaymentSchedule) => formatDate(item.dueDate),
    },
    {
      key: 'amount',
      header: 'Cuota',
      render: (item: PaymentSchedule) => <Currency amount={item.amount} />,
    },
    {
      key: 'principal',
      header: 'Capital',
      render: (item: PaymentSchedule) => <Currency amount={item.principal} />,
    },
    {
      key: 'interest',
      header: 'Interés',
      render: (item: PaymentSchedule) => <Currency amount={item.interest} />,
    },
    {
      key: 'status',
      header: 'Estado',
      render: (item: PaymentSchedule) => (
        <StatusBadge status={item.status} type="payment" />
      ),
    },
  ];

  if (isLoading) {
    return (
      <PageLayout>
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      </PageLayout>
    );
  }

  if (!loan) {
    return (
      <PageLayout>
        <div className="text-center py-12">
          <p className="text-gray-500">Préstamo no encontrado</p>
          <Link to={ROUTES.LOANS}>
            <Button variant="outline" className="mt-4">
              Volver a la lista
            </Button>
          </Link>
        </div>
      </PageLayout>
    );
  }

  const ltv = loan.property ? calculateLtv(loan.amount, loan.property.estimatedValue) : null;
  const canEdit = user?.role === 'Admin' || user?.role === 'CreditOfficer';

  return (
    <PageLayout>
      <div className="mb-6">
        <Link to={ROUTES.LOANS} className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a préstamos
        </Link>
      </div>

      <PageHeader
        title={`Préstamo ${loan.loanNumber}`}
        description={`${loan.borrower?.firstName} ${loan.borrower?.lastName}`}
        action={
          <div className="flex gap-2">
            <Link to={`${ROUTES.PAYMENT_NEW}?loanId=${loan.id}`}>
              <Button variant="outline">
                <DollarSign className="h-4 w-4 mr-2" />
                Registrar Pago
              </Button>
            </Link>
            {canEdit && (
              <Link to={ROUTES.LOAN_EDIT(loan.id)}>
                <Button variant="outline">
                  <Edit className="h-4 w-4 mr-2" />
                  Editar
                </Button>
              </Link>
            )}
            <Link to={ROUTES.COLLECTION_NEW(loan.id)}>
              <Button>
                <FileText className="h-4 w-4 mr-2" />
                Gestión de Cobro
              </Button>
            </Link>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Detalles del Préstamo</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm text-gray-500">Número de Préstamo</label>
                  <p className="font-medium">{loan.loanNumber}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Estado</label>
                  <div className="mt-1">
                    <StatusBadge status={loan.status} type="loan" />
                  </div>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Monto Original</label>
                  <p className="font-medium">{formatCurrency(loan.amount)}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Tasa de Interés</label>
                  <p className="font-medium">{loan.interestRate}% anual</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Plazo</label>
                  <p className="font-medium">{loan.termMonths} meses</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Cuota Mensual</label>
                  <p className="font-medium">{formatCurrency(loan.monthlyPayment || 0)}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Fecha de Inicio</label>
                  <p className="font-medium">{formatDate(loan.startDate)}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Fecha de Vencimiento</label>
                  <p className="font-medium">{formatDate(loan.endDate)}</p>
                </div>
                {ltv !== null && (
                  <div>
                    <label className="text-sm text-gray-500">LTV</label>
                    <p className={`font-medium ${ltv > 80 ? 'text-red-600' : ltv > 60 ? 'text-amber-600' : 'text-green-600'}`}>
                      {ltv.toFixed(1)}%
                    </p>
                  </div>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Calendario de Pagos</h3>
              {scheduleData?.data.length ? (
                <DataTable
                  columns={scheduleColumns}
                  data={scheduleData.data.slice(0, 12)}
                  keyExtractor={(item) => `${item.paymentNumber}`}
                />
              ) : (
                <p className="text-gray-500 text-center py-4">No hay calendario de pagos</p>
              )}
              {scheduleData?.data && scheduleData.data.length > 12 && (
                <p className="text-sm text-gray-500 mt-4 text-center">
                  Mostrando 12 de {scheduleData.data.length} cuotas
                </p>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Saldo</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-500">Saldo Pendiente</label>
                  <p className="text-2xl font-bold text-primary">
                    {formatCurrency(loan.outstandingBalance || loan.amount)}
                  </p>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Capital Pagado</span>
                  <span className="font-medium">{formatCurrency(loan.amount - (loan.outstandingBalance || loan.amount))}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${((loan.amount - (loan.outstandingBalance || loan.amount)) / loan.amount) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 text-center">
                  {(((loan.amount - (loan.outstandingBalance || loan.amount)) / loan.amount) * 100).toFixed(1)}% pagado
                </p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Prestatario</h3>
              {loan.borrower ? (
                <div className="space-y-3">
                  <div>
                    <Link
                      to={ROUTES.BORROWER_DETAIL(loan.borrower.id)}
                      className="text-blue-600 hover:underline font-medium"
                    >
                      {loan.borrower.firstName} {loan.borrower.lastName}
                    </Link>
                  </div>
                  <div className="text-sm text-gray-500">
                    <p>DPI: {loan.borrower.dpi}</p>
                    <p>{loan.borrower.phone}</p>
                    <p>{loan.borrower.email}</p>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">Sin prestatario asignado</p>
              )}
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Garantía</h3>
              {loan.property ? (
                <div className="space-y-3">
                  <div>
                    <Link
                      to={ROUTES.PROPERTY_DETAIL(loan.property.id)}
                      className="text-blue-600 hover:underline font-medium"
                    >
                      {loan.property.registryNumber}
                    </Link>
                  </div>
                  <div className="text-sm text-gray-500">
                    <p>{loan.property.propertyType}</p>
                    <p>{loan.property.address}</p>
                    <p className="font-medium text-gray-900">
                      Valor: {formatCurrency(loan.property.estimatedValue)}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">Sin garantía asignada</p>
              )}
            </div>
          </Card>

          {loan.status === 'Active' && loan.daysOverdue && loan.daysOverdue > 0 && (
            <Card className="border-red-200 bg-red-50">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <AlertTriangle className="h-6 w-6 text-red-500" />
                  <h3 className="text-lg font-semibold text-red-700">En Mora</h3>
                </div>
                <p className="text-red-600 font-medium">{loan.daysOverdue} días de atraso</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </PageLayout>
  );
}
