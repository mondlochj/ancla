import * as React from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { PageLayout, PageHeader } from '@/components/layout';
import {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  Input,
  Select,
  Alert,
} from '@/components/ui';
import { Currency } from '@/components/data';
import { ROUTES, MIN_LOAN_AMOUNT, MAX_LTV } from '@/lib/constants';
import { formatCurrency, formatPercentage, calculateMonthlyPayment } from '@/lib/utils';
import { ArrowLeft, Calculator } from 'lucide-react';

const loanFormSchema = z.object({
  borrowerId: z.string().min(1, 'Seleccione un prestatario'),
  propertyId: z.string().min(1, 'Seleccione una propiedad'),
  loanProductId: z.string().min(1, 'Seleccione un producto'),
  amount: z.number().min(MIN_LOAN_AMOUNT, `El monto mínimo es Q${MIN_LOAN_AMOUNT.toLocaleString()}`),
  termMonths: z.number().min(1, 'El plazo debe ser al menos 1 mes').max(60, 'El plazo máximo es 60 meses'),
  interestRate: z.number().min(0.01, 'La tasa debe ser mayor a 0').max(0.50, 'La tasa máxima es 50%'),
});

type LoanFormData = z.infer<typeof loanFormSchema>;

// Mock data - will be replaced with API calls
const mockBorrowers = [
  { value: '1', label: 'Juan Pérez - DPI: ****0101' },
  { value: '2', label: 'María García - DPI: ****0202' },
  { value: '3', label: 'Carlos López - DPI: ****0303' },
];

const mockProperties = [
  { value: '1', label: 'Finca 123, Folio 456, Libro 789 - Zona 10 (Valor: Q500,000)' },
  { value: '2', label: 'Finca 456, Folio 789, Libro 123 - Antigua (Valor: Q750,000)' },
];

const mockProducts = [
  { value: '1', label: 'Estándar (10% mensual, 6-24 meses)' },
  { value: '2', label: 'Premium (8% mensual, 12-36 meses)' },
];

export function LoanForm() {
  const navigate = useNavigate();
  const [error, setError] = React.useState<string | null>(null);
  const [propertyValue] = React.useState(500000); // Mock value

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<LoanFormData>({
    resolver: zodResolver(loanFormSchema),
    defaultValues: {
      borrowerId: '',
      propertyId: '',
      loanProductId: '',
      amount: MIN_LOAN_AMOUNT,
      termMonths: 12,
      interestRate: 0.10,
    },
  });

  const watchedAmount = watch('amount', MIN_LOAN_AMOUNT);
  const watchedTerm = watch('termMonths', 12);
  const watchedRate = watch('interestRate', 0.10);

  // Calculate LTV
  const ltv = propertyValue > 0 ? watchedAmount / propertyValue : 0;
  const isLtvValid = ltv <= MAX_LTV;

  // Calculate payment details
  const monthlyInterest = watchedAmount * watchedRate;
  const totalInterest = monthlyInterest * watchedTerm;
  const totalRepayment = watchedAmount + totalInterest;
  const monthlyPayment = calculateMonthlyPayment(watchedAmount, watchedRate * 12, watchedTerm);

  const onSubmit = async (data: LoanFormData) => {
    if (!isLtvValid) {
      setError(`El LTV no puede exceder ${formatPercentage(MAX_LTV)}`);
      return;
    }

    setError(null);
    try {
      // TODO: API call to create loan
      console.log('Creating loan:', data);
      navigate(ROUTES.LOANS);
    } catch (err) {
      setError('Error al crear el préstamo. Por favor intente de nuevo.');
    }
  };

  return (
    <PageLayout>
      <PageHeader
        title="Nuevo Préstamo"
        subtitle="Complete el formulario para crear un nuevo préstamo"
        actions={
          <Button
            variant="secondary"
            leftIcon={<ArrowLeft className="h-4 w-4" />}
            onClick={() => navigate(ROUTES.LOANS)}
          >
            Volver
          </Button>
        }
      />

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2 space-y-6">
            {error && (
              <Alert variant="danger" dismissible onDismiss={() => setError(null)}>
                {error}
              </Alert>
            )}

            {/* Borrower & Property */}
            <Card>
              <CardHeader>Prestatario y Garantía</CardHeader>
              <CardBody className="space-y-4">
                <Select
                  label="Prestatario"
                  options={mockBorrowers}
                  placeholder="Seleccione un prestatario"
                  error={errors.borrowerId?.message}
                  {...register('borrowerId')}
                />

                <Select
                  label="Propiedad (Garantía)"
                  options={mockProperties}
                  placeholder="Seleccione una propiedad"
                  error={errors.propertyId?.message}
                  {...register('propertyId')}
                />
              </CardBody>
            </Card>

            {/* Loan Details */}
            <Card>
              <CardHeader>Detalles del Préstamo</CardHeader>
              <CardBody className="space-y-4">
                <Select
                  label="Producto de Préstamo"
                  options={mockProducts}
                  placeholder="Seleccione un producto"
                  error={errors.loanProductId?.message}
                  {...register('loanProductId')}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Monto del Préstamo (Q)"
                    type="number"
                    min={MIN_LOAN_AMOUNT}
                    step={1000}
                    error={errors.amount?.message}
                    {...register('amount', { valueAsNumber: true })}
                  />

                  <Input
                    label="Plazo (meses)"
                    type="number"
                    min={1}
                    max={60}
                    error={errors.termMonths?.message}
                    {...register('termMonths', { valueAsNumber: true })}
                  />
                </div>

                <Input
                  label="Tasa de Interés Mensual (%)"
                  type="number"
                  min={1}
                  max={50}
                  step={0.5}
                  helperText="Ingrese el porcentaje (ej: 10 para 10%)"
                  error={errors.interestRate?.message}
                  {...register('interestRate', {
                    valueAsNumber: true,
                    setValueAs: (v) => v / 100,
                  })}
                />
              </CardBody>
            </Card>
          </div>

          {/* Calculation Preview */}
          <div>
            <Card className="sticky top-24">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Calculator className="h-4 w-4" />
                  Resumen del Préstamo
                </div>
              </CardHeader>
              <CardBody className="space-y-4">
                {/* LTV Warning */}
                {!isLtvValid && (
                  <Alert variant="danger">
                    El LTV ({formatPercentage(ltv)}) excede el máximo permitido ({formatPercentage(MAX_LTV)})
                  </Alert>
                )}

                <div className="space-y-3">
                  <SummaryRow
                    label="Monto del Préstamo"
                    value={<Currency amount={watchedAmount} />}
                  />
                  <SummaryRow
                    label="Valor de la Propiedad"
                    value={<Currency amount={propertyValue} />}
                  />
                  <SummaryRow
                    label="LTV"
                    value={formatPercentage(ltv)}
                    variant={isLtvValid ? 'default' : 'danger'}
                  />
                  <div className="border-t border-gray-200 pt-3">
                    <SummaryRow
                      label="Tasa Mensual"
                      value={formatPercentage(watchedRate)}
                    />
                    <SummaryRow
                      label="Plazo"
                      value={`${watchedTerm} meses`}
                    />
                  </div>
                  <div className="border-t border-gray-200 pt-3">
                    <SummaryRow
                      label="Interés Mensual"
                      value={<Currency amount={monthlyInterest} />}
                    />
                    <SummaryRow
                      label="Total Intereses"
                      value={<Currency amount={totalInterest} />}
                    />
                    <SummaryRow
                      label="Total a Pagar"
                      value={<Currency amount={totalRepayment} />}
                      highlight
                    />
                  </div>
                </div>
              </CardBody>
              <CardFooter>
                <Button
                  type="submit"
                  className="w-full"
                  isLoading={isSubmitting}
                  disabled={!isLtvValid}
                >
                  Crear Préstamo
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </form>
    </PageLayout>
  );
}

interface SummaryRowProps {
  label: string;
  value: React.ReactNode;
  variant?: 'default' | 'danger';
  highlight?: boolean;
}

function SummaryRow({ label, value, variant = 'default', highlight }: SummaryRowProps) {
  return (
    <div className={`flex justify-between items-center ${highlight ? 'font-semibold text-lg' : ''}`}>
      <span className="text-gray-600">{label}</span>
      <span className={variant === 'danger' ? 'text-danger font-medium' : ''}>{value}</span>
    </div>
  );
}

export default LoanForm;
