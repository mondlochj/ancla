import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Eye, Edit, MapPin, CheckCircle } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { DataTable, StatusBadge, EmptyState, Pagination, Currency } from '@/components/data';
import { Button, Input, Select, Card, Spinner } from '@/components/ui';
import { propertiesService } from '@/services';
import { VERIFICATION_STATUS_OPTIONS, ROUTES, DEPARTMENTS } from '@/lib/constants';
import type { Property } from '@/types';

interface PropertyFilters {
  page: number;
  pageSize: number;
  search?: string;
  verificationStatus?: string;
  propertyType?: string;
  department?: string;
}

export default function PropertyList() {
  const [filters, setFilters] = useState<PropertyFilters>({
    page: 1,
    pageSize: 10,
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['properties', filters],
    queryFn: () => propertiesService.getProperties(filters),
  });

  const columns = [
    {
      key: 'property',
      header: 'Propiedad',
      render: (property: Property) => (
        <div>
          <div className="font-medium text-gray-900">{property.registryNumber}</div>
          <div className="text-sm text-gray-500">{property.propertyType}</div>
        </div>
      ),
    },
    {
      key: 'location',
      header: 'Ubicación',
      render: (property: Property) => (
        <div className="flex items-start gap-2">
          <MapPin className="h-4 w-4 text-gray-400 mt-0.5" />
          <div className="text-sm">
            <div>{property.address}</div>
            <div className="text-gray-500">{property.municipality}, {property.department}</div>
          </div>
        </div>
      ),
    },
    {
      key: 'value',
      header: 'Valor',
      render: (property: Property) => <Currency amount={property.estimatedValue} />,
    },
    {
      key: 'area',
      header: 'Área',
      render: (property: Property) => (
        <span>{property.area?.toLocaleString()} m²</span>
      ),
    },
    {
      key: 'verificationStatus',
      header: 'Estado',
      render: (property: Property) => (
        <StatusBadge status={property.verificationStatus} type="verification" />
      ),
    },
    {
      key: 'actions',
      header: 'Acciones',
      render: (property: Property) => (
        <div className="flex items-center gap-2">
          <Link to={ROUTES.PROPERTY_DETAIL(property.id)}>
            <Button variant="ghost" size="sm">
              <Eye className="h-4 w-4" />
            </Button>
          </Link>
          <Link to={ROUTES.PROPERTY_EDIT(property.id)}>
            <Button variant="ghost" size="sm">
              <Edit className="h-4 w-4" />
            </Button>
          </Link>
          {property.verificationStatus === 'Pending' && (
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
        <div className="text-center text-red-600">Error al cargar propiedades</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Propiedades"
        description="Gestión de garantías inmobiliarias"
        action={
          <Link to={ROUTES.PROPERTY_NEW}>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nueva Propiedad
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
                placeholder="Buscar por número de registro..."
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
          <Select
            value={filters.department || ''}
            onChange={(e) => setFilters({ ...filters, department: e.target.value, page: 1 })}
            options={[
              { value: '', label: 'Todos los departamentos' },
              ...DEPARTMENTS.map(d => ({ value: d, label: d })),
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
          title="No hay propiedades"
          description="Comienza agregando tu primera propiedad"
          action={
            <Link to={ROUTES.PROPERTY_NEW}>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Nueva Propiedad
              </Button>
            </Link>
          }
        />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} keyExtractor={(p) => p.id} />
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
