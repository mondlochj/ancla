import { useNavigate, useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Save } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, Button, Input, Spinner, Alert } from '@/components/ui';
import { borrowersService } from '@/services';
import { ROUTES, DEPARTMENTS } from '@/lib/constants';
import type { BorrowerFormData } from '@/types';

const borrowerSchema = z.object({
  firstName: z.string().min(2, 'Nombre debe tener al menos 2 caracteres'),
  lastName: z.string().min(2, 'Apellido debe tener al menos 2 caracteres'),
  dpi: z.string().regex(/^\d{13}$/, 'DPI debe tener 13 dígitos'),
  nit: z.string().optional(),
  email: z.string().email('Email inválido').optional().or(z.literal('')),
  phone: z.string().min(8, 'Teléfono debe tener al menos 8 dígitos'),
  address: z.string().min(10, 'Dirección debe tener al menos 10 caracteres'),
  department: z.string().min(1, 'Departamento es requerido'),
  municipality: z.string().min(1, 'Municipio es requerido'),
  occupation: z.string().optional(),
  monthlyIncome: z.number().min(0, 'Ingreso mensual debe ser positivo').optional(),
  employerName: z.string().optional(),
  employerPhone: z.string().optional(),
});

type FormData = z.infer<typeof borrowerSchema>;

export default function BorrowerForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = !!id;

  const { data: borrower, isLoading: isLoadingBorrower } = useQuery({
    queryKey: ['borrower', id],
    queryFn: () => borrowersService.getBorrower(id!),
    enabled: isEditing,
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(borrowerSchema),
    defaultValues: borrower as FormData || {},
    values: borrower as FormData,
  });

  const createMutation = useMutation({
    mutationFn: (data: BorrowerFormData) => borrowersService.createBorrower(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['borrowers'] });
      navigate(ROUTES.BORROWERS);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<BorrowerFormData>) => borrowersService.updateBorrower(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['borrowers'] });
      queryClient.invalidateQueries({ queryKey: ['borrower', id] });
      navigate(ROUTES.BORROWER_DETAIL(id!));
    },
  });

  const onSubmit = (data: FormData) => {
    if (isEditing) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data as BorrowerFormData);
    }
  };

  const error = createMutation.error || updateMutation.error;

  if (isEditing && isLoadingBorrower) {
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
        <Link to={ROUTES.BORROWERS} className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a prestatarios
        </Link>
      </div>

      <PageHeader
        title={isEditing ? 'Editar Prestatario' : 'Nuevo Prestatario'}
        description={isEditing ? 'Actualiza la información del prestatario' : 'Registra un nuevo cliente'}
      />

      {error && (
        <Alert variant="error" className="mb-6">
          {(error as Error).message || 'Error al guardar prestatario'}
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información Personal</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Nombre"
                    {...register('firstName')}
                    error={errors.firstName?.message}
                  />
                  <Input
                    label="Apellido"
                    {...register('lastName')}
                    error={errors.lastName?.message}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="DPI"
                    {...register('dpi')}
                    error={errors.dpi?.message}
                    placeholder="1234567890123"
                    maxLength={13}
                  />
                  <Input
                    label="NIT (opcional)"
                    {...register('nit')}
                    error={errors.nit?.message}
                  />
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información de Contacto</h3>
              <div className="space-y-4">
                <Input
                  label="Email"
                  type="email"
                  {...register('email')}
                  error={errors.email?.message}
                />
                <Input
                  label="Teléfono"
                  {...register('phone')}
                  error={errors.phone?.message}
                />
                <Input
                  label="Dirección"
                  {...register('address')}
                  error={errors.address?.message}
                />
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Departamento
                    </label>
                    <select
                      {...register('department')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/50"
                    >
                      <option value="">Seleccionar...</option>
                      {DEPARTMENTS.map((dept) => (
                        <option key={dept} value={dept}>{dept}</option>
                      ))}
                    </select>
                    {errors.department && (
                      <p className="text-sm text-red-600 mt-1">{errors.department.message}</p>
                    )}
                  </div>
                  <Input
                    label="Municipio"
                    {...register('municipality')}
                    error={errors.municipality?.message}
                  />
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información Laboral</h3>
              <div className="space-y-4">
                <Input
                  label="Ocupación"
                  {...register('occupation')}
                  error={errors.occupation?.message}
                />
                <Input
                  label="Ingreso Mensual (Q)"
                  type="number"
                  {...register('monthlyIncome', { valueAsNumber: true })}
                  error={errors.monthlyIncome?.message}
                />
                <Input
                  label="Nombre del Empleador"
                  {...register('employerName')}
                  error={errors.employerName?.message}
                />
                <Input
                  label="Teléfono del Empleador"
                  {...register('employerPhone')}
                  error={errors.employerPhone?.message}
                />
              </div>
            </div>
          </Card>
        </div>

        <div className="mt-6 flex justify-end gap-4">
          <Link to={ROUTES.BORROWERS}>
            <Button variant="outline" type="button">
              Cancelar
            </Button>
          </Link>
          <Button type="submit" disabled={isSubmitting}>
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear Prestatario'}
          </Button>
        </div>
      </form>
    </PageLayout>
  );
}
