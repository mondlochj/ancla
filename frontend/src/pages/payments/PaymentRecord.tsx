import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Save, DollarSign } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, Button, Input, Select, Spinner, Alert } from '@/components/ui';
import { paymentsService, loansService } from '@/services';
import { ROUTES, PAYMENT_TYPE_OPTIONS, PAYMENT_METHOD_OPTIONS } from '@/lib/constants';
import { formatCurrency } from '@/lib/utils';
import type { PaymentFormData } from '@/types';

const paymentSchema = z.object({
  loanId: z.string().min(1, 'Préstamo es requerido'),
  amount: z.number().min(1, 'Monto debe ser mayor a 0'),
  paymentType: z.string().min(1, 'Tipo de pago es requerido'),
  paymentMethod: z.string().min(1, 'Método de pago es requerido'),
  paymentDate: z.string().min(1, 'Fecha de pago es requerida'),
  referenceNumber: z.string().optional(),
  notes: z.string().optional(),
});

type FormData = z.infer<typeof paymentSchema>;

export default function PaymentRecord() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const preselectedLoanId = searchParams.get('loanId');

  const { data: loansData, isLoading: isLoadingLoans } = useQuery({
    queryKey: ['loans-active'],
    queryFn: () => loansService.getLoans({ status: 'Active', pageSize: 100 }),
  });

  const { data: selectedLoan } = useQuery({
    queryKey: ['loan', preselectedLoanId],
    queryFn: () => loansService.getLoan(preselectedLoanId!),
    enabled: !!preselectedLoanId,
  });

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(paymentSchema),
    defaultValues: {
      loanId: preselectedLoanId || '',
      paymentDate: new Date().toISOString().split('T')[0],
      paymentType: 'Principal',
      paymentMethod: 'Cash',
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: PaymentFormData) => paymentsService.createPayment(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['loans'] });
      navigate(ROUTES.PAYMENTS);
    },
  });

  const onSubmit = (data: FormData) => {
    createMutation.mutate(data as PaymentFormData);
  };

  const watchedLoanId = watch('loanId');
  const watchedLoan = loansData?.data.find(l => l.id === watchedLoanId) || selectedLoan;

  if (isLoadingLoans) {
    return (
      <PageLayout>
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
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
        title="Registrar Pago"
        description="Registra un nuevo pago para un préstamo activo"
      />

      {createMutation.error && (
        <Alert variant="error" className="mb-6">
          {(createMutation.error as Error).message || 'Error al registrar pago'}
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Información del Pago</h3>
                <div className="space-y-4">
                  <Select
                    label="Préstamo"
                    {...register('loanId')}
                    error={errors.loanId?.message}
                    options={[
                      { value: '', label: 'Seleccionar préstamo...' },
                      ...(loansData?.data.map(l => ({
                        value: l.id,
                        label: `${l.loanNumber} - ${l.borrower?.firstName} ${l.borrower?.lastName}`,
                      })) || []),
                    ]}
                  />

                  <div className="grid grid-cols-2 gap-4">
                    <Input
                      label="Monto (Q)"
                      type="number"
                      step="0.01"
                      {...register('amount', { valueAsNumber: true })}
                      error={errors.amount?.message}
                    />
                    <Input
                      label="Fecha de Pago"
                      type="date"
                      {...register('paymentDate')}
                      error={errors.paymentDate?.message}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <Select
                      label="Tipo de Pago"
                      {...register('paymentType')}
                      error={errors.paymentType?.message}
                      options={PAYMENT_TYPE_OPTIONS}
                    />
                    <Select
                      label="Método de Pago"
                      {...register('paymentMethod')}
                      error={errors.paymentMethod?.message}
                      options={PAYMENT_METHOD_OPTIONS}
                    />
                  </div>

                  <Input
                    label="Número de Referencia"
                    {...register('referenceNumber')}
                    error={errors.referenceNumber?.message}
                    placeholder="Ej: Número de transferencia o recibo"
                  />

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notas
                    </label>
                    <textarea
                      {...register('notes')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50"
                      rows={3}
                      placeholder="Notas adicionales sobre el pago..."
                    />
                  </div>
                </div>
              </div>
            </Card>
          </div>

          <div>
            {watchedLoan && (
              <Card>
                <div className="p-6">
                  <h3 className="text-lg font-semibold mb-4">Resumen del Préstamo</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-gray-500">Préstamo</label>
                      <p className="font-medium">{watchedLoan.loanNumber}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Prestatario</label>
                      <p className="font-medium">
                        {watchedLoan.borrower?.firstName} {watchedLoan.borrower?.lastName}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Monto Original</label>
                      <p className="font-medium">{formatCurrency(watchedLoan.amount)}</p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Saldo Pendiente</label>
                      <p className="text-xl font-bold text-amber-600">
                        {formatCurrency(watchedLoan.outstandingBalance || watchedLoan.amount)}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm text-gray-500">Cuota Mensual</label>
                      <p className="font-medium">{formatCurrency(watchedLoan.monthlyPayment || 0)}</p>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            <Card className="mt-6">
              <div className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 bg-green-100 rounded-full">
                    <DollarSign className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold">Consejo</h4>
                    <p className="text-sm text-gray-500">
                      Verifica el monto y fecha antes de registrar
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-4">
          <Link to={ROUTES.PAYMENTS}>
            <Button variant="outline" type="button">
              Cancelar
            </Button>
          </Link>
          <Button type="submit" disabled={isSubmitting}>
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Registrando...' : 'Registrar Pago'}
          </Button>
        </div>
      </form>
    </PageLayout>
  );
}
