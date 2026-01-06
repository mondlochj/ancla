import { useNavigate, useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Save, Phone, Calendar, Mail, FileText } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, Button, Input, Select, Spinner, Alert } from '@/components/ui';
import { loansService } from '@/services';
import { ROUTES } from '@/lib/constants';
import { formatCurrency } from '@/lib/utils';
import api from '@/services/api';

const collectionSchema = z.object({
  actionType: z.string().min(1, 'Tipo de acción es requerido'),
  actionDate: z.string().min(1, 'Fecha es requerida'),
  notes: z.string().min(10, 'Las notas deben tener al menos 10 caracteres'),
  result: z.string().optional(),
  promisedAmount: z.number().optional(),
  promisedDate: z.string().optional(),
  followUpDate: z.string().optional(),
  followUpNotes: z.string().optional(),
});

type FormData = z.infer<typeof collectionSchema>;

export default function CollectionForm() {
  const { loanId } = useParams<{ loanId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: loan, isLoading: isLoadingLoan } = useQuery({
    queryKey: ['loan', loanId],
    queryFn: () => loansService.getLoan(loanId!),
    enabled: !!loanId,
  });

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(collectionSchema),
    defaultValues: {
      actionDate: new Date().toISOString().split('T')[0],
      actionType: 'Call',
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await api.post(`/api/collections`, { ...data, loanId });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collections'] });
      queryClient.invalidateQueries({ queryKey: ['loan', loanId] });
      navigate(ROUTES.LOAN_DETAIL(loanId!));
    },
  });

  const onSubmit = (data: FormData) => {
    createMutation.mutate(data);
  };

  const watchedActionType = watch('actionType');

  const getActionIcon = () => {
    switch (watchedActionType) {
      case 'Call': return <Phone className="h-5 w-5" />;
      case 'Visit': return <Calendar className="h-5 w-5" />;
      case 'Email': return <Mail className="h-5 w-5" />;
      case 'Letter': return <FileText className="h-5 w-5" />;
      default: return null;
    }
  };

  if (isLoadingLoan) {
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
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="mb-6">
        <Link to={ROUTES.LOAN_DETAIL(loanId!)} className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver al préstamo
        </Link>
      </div>

      <PageHeader
        title="Nueva Gestión de Cobro"
        description={`Préstamo: ${loan.loanNumber}`}
      />

      {createMutation.error && (
        <Alert variant="error" className="mb-6">
          {(createMutation.error as Error).message || 'Error al registrar gestión'}
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  {getActionIcon()}
                  Información de la Acción
                </h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <Select
                      label="Tipo de Acción"
                      {...register('actionType')}
                      error={errors.actionType?.message}
                      options={[
                        { value: 'Call', label: 'Llamada telefónica' },
                        { value: 'Visit', label: 'Visita domiciliar' },
                        { value: 'Email', label: 'Correo electrónico' },
                        { value: 'Letter', label: 'Carta de cobro' },
                      ]}
                    />
                    <Input
                      label="Fecha"
                      type="date"
                      {...register('actionDate')}
                      error={errors.actionDate?.message}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notas de la Gestión *
                    </label>
                    <textarea
                      {...register('notes')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50"
                      rows={4}
                      placeholder="Describe el resultado de la gestión, qué se habló, compromisos, etc."
                    />
                    {errors.notes && (
                      <p className="text-sm text-red-600 mt-1">{errors.notes.message}</p>
                    )}
                  </div>

                  <Select
                    label="Resultado"
                    {...register('result')}
                    error={errors.result?.message}
                    options={[
                      { value: '', label: 'Seleccionar...' },
                      { value: 'Successful', label: 'Exitoso - Cliente contactado' },
                      { value: 'NoAnswer', label: 'Sin respuesta' },
                      { value: 'WrongNumber', label: 'Número incorrecto' },
                      { value: 'Promise', label: 'Promesa de pago' },
                      { value: 'Refused', label: 'Cliente se negó' },
                      { value: 'NotFound', label: 'Cliente no localizado' },
                    ]}
                  />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Promesa de Pago</h3>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Monto Prometido (Q)"
                    type="number"
                    step="0.01"
                    {...register('promisedAmount', { valueAsNumber: true })}
                    error={errors.promisedAmount?.message}
                  />
                  <Input
                    label="Fecha Prometida"
                    type="date"
                    {...register('promisedDate')}
                    error={errors.promisedDate?.message}
                  />
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Seguimiento</h3>
                <div className="space-y-4">
                  <Input
                    label="Fecha de Seguimiento"
                    type="date"
                    {...register('followUpDate')}
                    error={errors.followUpDate?.message}
                  />
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notas de Seguimiento
                    </label>
                    <textarea
                      {...register('followUpNotes')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50"
                      rows={2}
                      placeholder="Qué acciones se deben tomar en el seguimiento..."
                    />
                  </div>
                </div>
              </div>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Información del Préstamo</h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-500">Préstamo</label>
                    <p className="font-medium">{loan.loanNumber}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Prestatario</label>
                    <p className="font-medium">
                      {loan.borrower?.firstName} {loan.borrower?.lastName}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Teléfono</label>
                    <p className="font-medium">{loan.borrower?.phone || 'N/A'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Saldo Pendiente</label>
                    <p className="text-xl font-bold text-amber-600">
                      {formatCurrency(loan.outstandingBalance || loan.amount)}
                    </p>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">Estado del Préstamo</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Estado</span>
                    <span className="font-medium">{loan.status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Días en mora</span>
                    <span className="font-medium text-red-600">{loan.daysOverdue || 0}</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-4">
          <Link to={ROUTES.LOAN_DETAIL(loanId!)}>
            <Button variant="outline" type="button">
              Cancelar
            </Button>
          </Link>
          <Button type="submit" disabled={isSubmitting}>
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Guardando...' : 'Registrar Gestión'}
          </Button>
        </div>
      </form>
    </PageLayout>
  );
}
