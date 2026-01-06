import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Search, Filter, Eye, Phone, Calendar } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { DataTable, EmptyState, Pagination } from '@/components/data';
import { Button, Input, Select, Card, Spinner, Badge } from '@/components/ui';
import { formatDate } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import api from '@/services/api';
import type { CollectionAction, PaginatedResponse } from '@/types';

interface CollectionFilters {
  page: number;
  pageSize: number;
  search?: string;
  actionType?: string;
  status?: string;
}

export default function CollectionList() {
  const [filters, setFilters] = useState<CollectionFilters>({
    page: 1,
    pageSize: 10,
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['collections', filters],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<CollectionAction>>('/api/collections', { params: filters });
      return response.data;
    },
  });

  const getActionTypeIcon = (type: string) => {
    switch (type) {
      case 'Call':
        return <Phone className="h-4 w-4" />;
      case 'Visit':
        return <Calendar className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const columns = [
    {
      key: 'loan',
      header: 'Préstamo',
      render: (action: CollectionAction) => (
        <div>
          <Link to={ROUTES.LOAN_DETAIL(action.loanId)} className="text-blue-600 hover:underline font-medium">
            {action.loanNumber || action.loanId}
          </Link>
          <div className="text-sm text-gray-500">
            {action.borrowerName}
          </div>
        </div>
      ),
    },
    {
      key: 'actionType',
      header: 'Tipo',
      render: (action: CollectionAction) => (
        <div className="flex items-center gap-2">
          {getActionTypeIcon(action.actionType)}
          <span>{action.actionType}</span>
        </div>
      ),
    },
    {
      key: 'date',
      header: 'Fecha',
      render: (action: CollectionAction) => formatDate(action.actionDate),
    },
    {
      key: 'result',
      header: 'Resultado',
      render: (action: CollectionAction) => (
        <Badge variant={action.result === 'Successful' ? 'success' : action.result === 'Failed' ? 'danger' : 'default'}>
          {action.result || 'Pendiente'}
        </Badge>
      ),
    },
    {
      key: 'agent',
      header: 'Agente',
      render: (action: CollectionAction) => action.agentName || '-',
    },
    {
      key: 'followUp',
      header: 'Seguimiento',
      render: (action: CollectionAction) => (
        action.followUpDate ? (
          <div className="text-sm">
            <div>{formatDate(action.followUpDate)}</div>
            <div className="text-gray-500">{action.followUpNotes?.substring(0, 30)}...</div>
          </div>
        ) : '-'
      ),
    },
    {
      key: 'actions',
      header: 'Acciones',
      render: (action: CollectionAction) => (
        <Link to={ROUTES.COLLECTION_DETAIL(action.id)}>
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
        </Link>
      ),
    },
  ];

  if (error) {
    return (
      <PageLayout>
        <div className="text-center text-red-600">Error al cargar gestiones de cobro</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Gestión de Cobros"
        description="Historial de acciones de cobranza"
      />

      <Card className="mb-6">
        <div className="p-4 flex flex-wrap gap-4">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Buscar por préstamo o prestatario..."
                className="pl-10"
                value={filters.search || ''}
                onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
              />
            </div>
          </div>
          <Select
            value={filters.actionType || ''}
            onChange={(e) => setFilters({ ...filters, actionType: e.target.value, page: 1 })}
            options={[
              { value: '', label: 'Todos los tipos' },
              { value: 'Call', label: 'Llamada' },
              { value: 'Visit', label: 'Visita' },
              { value: 'Letter', label: 'Carta' },
              { value: 'Email', label: 'Email' },
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
          title="No hay gestiones de cobro"
          description="Las gestiones de cobro aparecerán aquí"
        />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} keyExtractor={(a) => a.id} />
          <div className="mt-4">
            <Pagination
              currentPage={filters.page}
              totalPages={data.totalPages}
              onPageChange={(page) => setFilters({ ...filters, page })}
            />
          </div>
        </>
      )}
    </PageLayout>
  );
}
