import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Eye, Edit, CheckCircle } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { DataTable, StatusBadge, EmptyState, Pagination } from '@/components/data';
import { Button, Input, Select, Card, Spinner } from '@/components/ui';
import { borrowersService } from '@/services';
import { formatDate } from '@/lib/utils';
import { VERIFICATION_STATUS_OPTIONS, ROUTES } from '@/lib/constants';
import type { Borrower, BorrowerFilters } from '@/types';

export default function BorrowerList() {
  const [filters, setFilters] = useState<BorrowerFilters>({
    page: 1,
    pageSize: 10,
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['borrowers', filters],
    queryFn: () => borrowersService.getBorrowers(filters),
  });

  const columns = [
    {
      key: 'name',
      header: 'Nombre',
      render: (borrower: Borrower) => (
        <div>
          <div className="font-medium text-gray-900">
            {borrower.firstName} {borrower.lastName}
          </div>
          <div className="text-sm text-gray-500">{borrower.dpi}</div>
        </div>
      ),
    },
    {
      key: 'contact',
      header: 'Contacto',
      render: (borrower: Borrower) => (
        <div className="text-sm">
          <div>{borrower.email}</div>
          <div className="text-gray-500">{borrower.phone}</div>
        </div>
      ),
    },
    {
      key: 'activeLoans',
      header: 'Préstamos Activos',
      render: (borrower: Borrower) => (
        <span className="font-medium">{borrower.activeLoans || 0}</span>
      ),
    },
    {
      key: 'verificationStatus',
      header: 'Estado',
      render: (borrower: Borrower) => (
        <StatusBadge status={borrower.verificationStatus} type="verification" />
      ),
    },
    {
      key: 'createdAt',
      header: 'Registrado',
      render: (borrower: Borrower) => formatDate(borrower.createdAt),
    },
    {
      key: 'actions',
      header: 'Acciones',
      render: (borrower: Borrower) => (
        <div className="flex items-center gap-2">
          <Link to={ROUTES.BORROWER_DETAIL(borrower.id)}>
            <Button variant="ghost" size="sm">
              <Eye className="h-4 w-4" />
            </Button>
          </Link>
          <Link to={ROUTES.BORROWER_EDIT(borrower.id)}>
            <Button variant="ghost" size="sm">
              <Edit className="h-4 w-4" />
            </Button>
          </Link>
          {borrower.verificationStatus === 'Pending' && (
            <Button variant="ghost" size="sm" className="text-green-600">
              <CheckCircle className="h-4 w-4" />
            </Button>
          )}
        </div>
      ),
    },
  ];

  if (error) {
    return (
      <PageLayout>
        <div className="text-center text-red-600">Error al cargar prestatarios</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Prestatarios"
        description="Gestión de clientes y prestatarios"
        action={
          <Link to={ROUTES.BORROWER_NEW}>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nuevo Prestatario
            </Button>
          </Link>
        }
      />

      <Card className="mb-6">
        <div className="p-4 flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar por nombre o DPI..."
                className="pl-10"
                value={filters.search || ''}
                onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
              />
            </div>
          </div>
          <Select
            value={filters.verificationStatus || ''}
            onChange={(e) => setFilters({ ...filters, verificationStatus: e.target.value, page: 1 })}
            options={[
              { value: '', label: 'Todos los estados' },
              ...VERIFICATION_STATUS_OPTIONS,
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
          title="No hay prestatarios"
          description="Comienza agregando tu primer prestatario"
          action={
            <Link to={ROUTES.BORROWER_NEW}>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Nuevo Prestatario
              </Button>
            </Link>
          }
        />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} keyExtractor={(b) => b.id} />
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
