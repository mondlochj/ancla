import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter, Eye, Download, FileText, File, Image } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { DataTable, EmptyState, Pagination } from '@/components/data';
import { Button, Input, Select, Card, Spinner, Badge } from '@/components/ui';
import { formatDate } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import api from '@/services/api';
import type { Document, PaginatedResponse } from '@/types';

interface DocumentFilters {
  page: number;
  pageSize: number;
  search?: string;
  documentType?: string;
  status?: string;
}

export default function DocumentList() {
  const [filters, setFilters] = useState<DocumentFilters>({
    page: 1,
    pageSize: 10,
  });

  const { data, isLoading, error } = useQuery({
    queryKey: ['documents', filters],
    queryFn: async () => {
      const response = await api.get<PaginatedResponse<Document>>('/api/documents', { params: filters });
      return response.data;
    },
  });

  const getDocumentIcon = (type: string) => {
    if (type.includes('image')) return <Image className="h-5 w-5 text-blue-500" />;
    if (type.includes('pdf')) return <FileText className="h-5 w-5 text-red-500" />;
    return <File className="h-5 w-5 text-gray-500" />;
  };

  const columns = [
    {
      key: 'document',
      header: 'Documento',
      render: (doc: Document) => (
        <div className="flex items-center gap-3">
          {getDocumentIcon(doc.documentType)}
          <div>
            <div className="font-medium">{doc.name}</div>
            <div className="text-sm text-gray-500">{doc.documentType}</div>
          </div>
        </div>
      ),
    },
    {
      key: 'entity',
      header: 'Relacionado a',
      render: (doc: Document) => (
        <div className="text-sm">
          {doc.loanId && (
            <Link to={ROUTES.LOAN_DETAIL(doc.loanId)} className="text-blue-600 hover:underline">
              Préstamo: {doc.loanNumber}
            </Link>
          )}
          {doc.borrowerId && (
            <Link to={ROUTES.BORROWER_DETAIL(doc.borrowerId)} className="text-blue-600 hover:underline">
              Prestatario: {doc.borrowerName}
            </Link>
          )}
          {doc.propertyId && (
            <Link to={ROUTES.PROPERTY_DETAIL(doc.propertyId)} className="text-blue-600 hover:underline">
              Propiedad: {doc.propertyNumber}
            </Link>
          )}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Estado',
      render: (doc: Document) => (
        <Badge variant={doc.status === 'Active' ? 'success' : doc.status === 'Expired' ? 'danger' : 'default'}>
          {doc.status}
        </Badge>
      ),
    },
    {
      key: 'uploadedBy',
      header: 'Subido por',
      render: (doc: Document) => (
        <div className="text-sm">
          <div>{doc.uploadedByName}</div>
          <div className="text-gray-500">{formatDate(doc.createdAt)}</div>
        </div>
      ),
    },
    {
      key: 'actions',
      header: 'Acciones',
      render: (doc: Document) => (
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ];

  if (error) {
    return (
      <PageLayout>
        <div className="text-center text-red-600">Error al cargar documentos</div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <PageHeader
        title="Documentos Legales"
        description="Gestión de documentación legal y contratos"
        action={
          <Link to={ROUTES.DOCUMENT_NEW}>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Subir Documento
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
                placeholder="Buscar documentos..."
                className="pl-10"
                value={filters.search || ''}
                onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
              />
            </div>
          </div>
          <Select
            value={filters.documentType || ''}
            onChange={(e) => setFilters({ ...filters, documentType: e.target.value, page: 1 })}
            options={[
              { value: '', label: 'Todos los tipos' },
              { value: 'Contract', label: 'Contrato' },
              { value: 'DPI', label: 'DPI' },
              { value: 'PropertyDeed', label: 'Escritura' },
              { value: 'Appraisal', label: 'Avalúo' },
              { value: 'Other', label: 'Otro' },
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
          title="No hay documentos"
          description="Comienza subiendo tu primer documento"
          action={
            <Link to={ROUTES.DOCUMENT_NEW}>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Subir Documento
              </Button>
            </Link>
          }
        />
      ) : (
        <>
          <DataTable columns={columns} data={data.data} keyExtractor={(d) => d.id} />
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
