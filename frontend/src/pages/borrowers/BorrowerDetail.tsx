import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Edit, Phone, Mail, MapPin, CreditCard } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, Button, Spinner } from '@/components/ui';
import { StatusBadge, Currency, DataTable } from '@/components/data';
import { borrowersService } from '@/services';
import { formatDate, formatCurrency } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import type { Loan } from '@/types';

export default function BorrowerDetail() {
  const { id } = useParams<{ id: string }>();

  const { data: borrower, isLoading } = useQuery({
    queryKey: ['borrower', id],
    queryFn: () => borrowersService.getBorrower(id!),
    enabled: !!id,
  });

  const { data: loansData } = useQuery({
    queryKey: ['borrower-loans', id],
    queryFn: () => borrowersService.getBorrowerLoans(id!),
    enabled: !!id,
  });

  const loanColumns = [
    {
      key: 'loanNumber',
      header: 'Número',
      render: (loan: Loan) => (
        <Link to={ROUTES.LOAN_DETAIL(loan.id)} className="text-blue-600 hover:underline font-medium">
          {loan.loanNumber}
        </Link>
      ),
    },
    {
      key: 'amount',
      header: 'Monto',
      render: (loan: Loan) => <Currency amount={loan.amount} />,
    },
    {
      key: 'status',
      header: 'Estado',
      render: (loan: Loan) => <StatusBadge status={loan.status} type="loan" />,
    },
    {
      key: 'startDate',
      header: 'Fecha Inicio',
      render: (loan: Loan) => formatDate(loan.startDate),
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

  if (!borrower) {
    return (
      <PageLayout>
        <div className="text-center py-12">
          <p className="text-gray-500">Prestatario no encontrado</p>
          <Link to={ROUTES.BORROWERS}>
            <Button variant="outline" className="mt-4">
              Volver a la lista
            </Button>
          </Link>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="mb-6">
        <Link to={ROUTES.BORROWERS} className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a prestatarios
        </Link>
      </div>

      <PageHeader
        title={`${borrower.firstName} ${borrower.lastName}`}
        description={`DPI: ${borrower.dpi}`}
        action={
          <div className="flex gap-2">
            <Link to={ROUTES.BORROWER_EDIT(borrower.id)}>
              <Button variant="outline">
                <Edit className="h-4 w-4 mr-2" />
                Editar
              </Button>
            </Link>
            <Link to={`${ROUTES.LOAN_NEW}?borrowerId=${borrower.id}`}>
              <Button>
                <CreditCard className="h-4 w-4 mr-2" />
                Nuevo Préstamo
              </Button>
            </Link>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información Personal</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-500">Nombre Completo</label>
                  <p className="font-medium">{borrower.firstName} {borrower.lastName}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">DPI</label>
                  <p className="font-medium">{borrower.dpi}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">NIT</label>
                  <p className="font-medium">{borrower.nit || 'No registrado'}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Estado de Verificación</label>
                  <div className="mt-1">
                    <StatusBadge status={borrower.verificationStatus} type="verification" />
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información de Contacto</h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-gray-400" />
                  <span>{borrower.email}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Phone className="h-5 w-5 text-gray-400" />
                  <span>{borrower.phone}</span>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
                  <span>{borrower.address}</span>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Préstamos</h3>
              {loansData?.data.length ? (
                <DataTable columns={loanColumns} data={loansData.data} keyExtractor={(l) => l.id} />
              ) : (
                <p className="text-gray-500 text-center py-4">No hay préstamos registrados</p>
              )}
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Resumen</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-500">Préstamos Activos</label>
                  <p className="text-2xl font-bold text-primary">{borrower.activeLoans || 0}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Total Prestado</label>
                  <p className="text-xl font-semibold">{formatCurrency(borrower.totalLoaned || 0)}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Saldo Pendiente</label>
                  <p className="text-xl font-semibold text-amber-600">{formatCurrency(borrower.outstandingBalance || 0)}</p>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información del Sistema</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <label className="text-gray-500">Fecha de Registro</label>
                  <p>{formatDate(borrower.createdAt)}</p>
                </div>
                <div>
                  <label className="text-gray-500">Última Actualización</label>
                  <p>{formatDate(borrower.updatedAt)}</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </PageLayout>
  );
}
