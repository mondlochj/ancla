import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, CardBody, Button, Input, Select } from '@/components/ui';
import { DataTable, Currency, StatusBadge, Pagination } from '@/components/data';
import type { Column } from '@/components/data';
import { ROUTES, LOAN_STATUSES } from '@/lib/constants';
import { formatDate } from '@/lib/utils';
import type { Loan, LoanStatus } from '@/types';
import { Plus, Search } from 'lucide-react';

// Mock data - will be replaced with API calls
const mockLoans: Loan[] = [
  {
    id: '1',
    referenceNumber: 'AC-2401-A1B2',
    borrower: { id: '1', fullName: 'Juan Pérez', dpi: '1234567890101' } as Loan['borrower'],
    property: { id: '1', address: 'Zona 10, Guatemala' } as Loan['property'],
    loanProduct: { id: '1', name: 'Estándar' } as Loan['loanProduct'],
    amount: 150000,
    termMonths: 12,
    interestRate: 0.10,
    ltv: 0.35,
    status: 'Active',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    referenceNumber: 'AC-2401-C3D4',
    borrower: { id: '2', fullName: 'María García', dpi: '9876543210101' } as Loan['borrower'],
    property: { id: '2', address: 'Antigua Guatemala' } as Loan['property'],
    loanProduct: { id: '1', name: 'Premium' } as Loan['loanProduct'],
    amount: 250000,
    termMonths: 24,
    interestRate: 0.08,
    ltv: 0.28,
    status: 'UnderReview',
    createdAt: '2024-01-14T10:00:00Z',
    updatedAt: '2024-01-14T10:00:00Z',
  },
  {
    id: '3',
    referenceNumber: 'AC-2401-E5F6',
    borrower: { id: '3', fullName: 'Carlos López', dpi: '5555555550101' } as Loan['borrower'],
    property: { id: '3', address: 'Escuintla' } as Loan['property'],
    loanProduct: { id: '1', name: 'Estándar' } as Loan['loanProduct'],
    amount: 100000,
    termMonths: 6,
    interestRate: 0.12,
    ltv: 0.40,
    status: 'Approved',
    createdAt: '2024-01-13T10:00:00Z',
    updatedAt: '2024-01-13T10:00:00Z',
  },
];

export function LoanList() {
  const navigate = useNavigate();
  const [search, setSearch] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState<LoanStatus | ''>('');
  const [currentPage, setCurrentPage] = React.useState(1);
  const [sortColumn, setSortColumn] = React.useState<string>('createdAt');
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('desc');

  const columns: Column<Loan>[] = [
    {
      key: 'referenceNumber',
      header: 'Referencia',
      sortable: true,
      render: (loan) => (
        <span className="font-medium text-secondary">{loan.referenceNumber}</span>
      ),
    },
    {
      key: 'borrower',
      header: 'Prestatario',
      sortable: true,
      render: (loan) => (
        <div>
          <div className="font-medium">{loan.borrower.fullName}</div>
          <div className="text-xs text-gray-500">
            DPI: ****{loan.borrower.dpi?.slice(-4)}
          </div>
        </div>
      ),
    },
    {
      key: 'amount',
      header: 'Monto',
      sortable: true,
      render: (loan) => <Currency amount={loan.amount} />,
      className: 'text-right',
    },
    {
      key: 'termMonths',
      header: 'Plazo',
      render: (loan) => `${loan.termMonths} meses`,
    },
    {
      key: 'ltv',
      header: 'LTV',
      render: (loan) => `${(loan.ltv * 100).toFixed(1)}%`,
    },
    {
      key: 'status',
      header: 'Estado',
      render: (loan) => <StatusBadge status={loan.status} type="loan" />,
    },
    {
      key: 'createdAt',
      header: 'Fecha',
      sortable: true,
      render: (loan) => formatDate(loan.createdAt),
    },
  ];

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  // Filter loans
  const filteredLoans = mockLoans.filter((loan) => {
    const matchesSearch =
      !search ||
      loan.referenceNumber.toLowerCase().includes(search.toLowerCase()) ||
      loan.borrower.fullName.toLowerCase().includes(search.toLowerCase());

    const matchesStatus = !statusFilter || loan.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const statusOptions = [
    { value: '', label: 'Todos los estados' },
    ...LOAN_STATUSES.map((s) => ({ value: s.value, label: s.label })),
  ];

  return (
    <PageLayout>
      <PageHeader
        title="Préstamos"
        subtitle={`${filteredLoans.length} préstamos encontrados`}
        actions={
          <Button
            leftIcon={<Plus className="h-4 w-4" />}
            onClick={() => navigate(ROUTES.LOAN_CREATE)}
          >
            Nuevo Préstamo
          </Button>
        }
      />

      <Card>
        <CardBody>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1">
              <Input
                placeholder="Buscar por referencia o nombre..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                leftIcon={<Search className="h-4 w-4" />}
              />
            </div>
            <div className="w-full sm:w-48">
              <Select
                options={statusOptions}
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as LoanStatus | '')}
              />
            </div>
          </div>

          {/* Table */}
          <DataTable
            columns={columns}
            data={filteredLoans}
            keyExtractor={(loan) => loan.id}
            onRowClick={(loan) => navigate(`/loans/${loan.id}`)}
            sortColumn={sortColumn}
            sortDirection={sortDirection}
            onSort={handleSort}
          />

          {/* Pagination */}
          <div className="mt-6">
            <Pagination
              currentPage={currentPage}
              totalPages={5}
              onPageChange={setCurrentPage}
            />
          </div>
        </CardBody>
      </Card>
    </PageLayout>
  );
}

export default LoanList;
