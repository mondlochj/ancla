import { useNavigate, useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ArrowLeft, Save } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, Button, Input, Select, Spinner, Alert } from '@/components/ui';
import { propertiesService, borrowersService } from '@/services';
import { ROUTES, DEPARTMENTS, PROPERTY_TYPE_OPTIONS } from '@/lib/constants';
import type { PropertyFormData } from '@/types';

const propertySchema = z.object({
  registryNumber: z.string().min(1, 'Número de registro es requerido'),
  finca: z.string().optional(),
  folio: z.string().optional(),
  libro: z.string().optional(),
  propertyType: z.string().min(1, 'Tipo de propiedad es requerido'),
  address: z.string().min(10, 'Dirección debe tener al menos 10 caracteres'),
  department: z.string().min(1, 'Departamento es requerido'),
  municipality: z.string().min(1, 'Municipio es requerido'),
  area: z.number().min(1, 'Área es requerida'),
  constructionArea: z.number().optional(),
  estimatedValue: z.number().min(1, 'Valor estimado es requerido'),
  appraisalValue: z.number().optional(),
  borrowerId: z.string().optional(),
  bedrooms: z.number().optional(),
  bathrooms: z.number().optional(),
  parkingSpaces: z.number().optional(),
  yearBuilt: z.number().optional(),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
});

type FormData = z.infer<typeof propertySchema>;

export default function PropertyForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditing = !!id;

  const { data: property, isLoading: isLoadingProperty } = useQuery({
    queryKey: ['property', id],
    queryFn: () => propertiesService.getProperty(id!),
    enabled: isEditing,
  });

  const { data: borrowersData } = useQuery({
    queryKey: ['borrowers-list'],
    queryFn: () => borrowersService.getBorrowers({ pageSize: 100 }),
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({
    resolver: zodResolver(propertySchema),
    defaultValues: property as FormData || {},
    values: property as FormData,
  });

  const createMutation = useMutation({
    mutationFn: (data: PropertyFormData) => propertiesService.createProperty(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] });
      navigate(ROUTES.PROPERTIES);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: Partial<PropertyFormData>) => propertiesService.updateProperty(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['properties'] });
      queryClient.invalidateQueries({ queryKey: ['property', id] });
      navigate(ROUTES.PROPERTY_DETAIL(id!));
    },
  });

  const onSubmit = (data: FormData) => {
    if (isEditing) {
      updateMutation.mutate(data);
    } else {
      createMutation.mutate(data as PropertyFormData);
    }
  };

  const error = createMutation.error || updateMutation.error;

  if (isEditing && isLoadingProperty) {
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
        <Link to={ROUTES.PROPERTIES} className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a propiedades
        </Link>
      </div>

      <PageHeader
        title={isEditing ? 'Editar Propiedad' : 'Nueva Propiedad'}
        description={isEditing ? 'Actualiza la información de la propiedad' : 'Registra una nueva garantía'}
      />

      {error && (
        <Alert variant="error" className="mb-6">
          {(error as Error).message || 'Error al guardar propiedad'}
        </Alert>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información de Registro</h3>
              <div className="space-y-4">
                <Input
                  label="Número de Registro"
                  {...register('registryNumber')}
                  error={errors.registryNumber?.message}
                />
                <div className="grid grid-cols-3 gap-4">
                  <Input
                    label="Finca"
                    {...register('finca')}
                    error={errors.finca?.message}
                  />
                  <Input
                    label="Folio"
                    {...register('folio')}
                    error={errors.folio?.message}
                  />
                  <Input
                    label="Libro"
                    {...register('libro')}
                    error={errors.libro?.message}
                  />
                </div>
                <Select
                  label="Tipo de Propiedad"
                  {...register('propertyType')}
                  error={errors.propertyType?.message}
                  options={[
                    { value: '', label: 'Seleccionar...' },
                    ...PROPERTY_TYPE_OPTIONS,
                  ]}
                />
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Ubicación</h3>
              <div className="space-y-4">
                <Input
                  label="Dirección"
                  {...register('address')}
                  error={errors.address?.message}
                />
                <div className="grid grid-cols-2 gap-4">
                  <Select
                    label="Departamento"
                    {...register('department')}
                    error={errors.department?.message}
                    options={[
                      { value: '', label: 'Seleccionar...' },
                      ...DEPARTMENTS.map(d => ({ value: d, label: d })),
                    ]}
                  />
                  <Input
                    label="Municipio"
                    {...register('municipality')}
                    error={errors.municipality?.message}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Latitud"
                    type="number"
                    step="any"
                    {...register('latitude', { valueAsNumber: true })}
                    error={errors.latitude?.message}
                  />
                  <Input
                    label="Longitud"
                    type="number"
                    step="any"
                    {...register('longitude', { valueAsNumber: true })}
                    error={errors.longitude?.message}
                  />
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Características</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Área Total (m²)"
                    type="number"
                    {...register('area', { valueAsNumber: true })}
                    error={errors.area?.message}
                  />
                  <Input
                    label="Área de Construcción (m²)"
                    type="number"
                    {...register('constructionArea', { valueAsNumber: true })}
                    error={errors.constructionArea?.message}
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <Input
                    label="Habitaciones"
                    type="number"
                    {...register('bedrooms', { valueAsNumber: true })}
                    error={errors.bedrooms?.message}
                  />
                  <Input
                    label="Baños"
                    type="number"
                    {...register('bathrooms', { valueAsNumber: true })}
                    error={errors.bathrooms?.message}
                  />
                  <Input
                    label="Parqueos"
                    type="number"
                    {...register('parkingSpaces', { valueAsNumber: true })}
                    error={errors.parkingSpaces?.message}
                  />
                </div>
                <Input
                  label="Año de Construcción"
                  type="number"
                  {...register('yearBuilt', { valueAsNumber: true })}
                  error={errors.yearBuilt?.message}
                />
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Valuación y Propietario</h3>
              <div className="space-y-4">
                <Input
                  label="Valor Estimado (Q)"
                  type="number"
                  {...register('estimatedValue', { valueAsNumber: true })}
                  error={errors.estimatedValue?.message}
                />
                <Input
                  label="Valor de Avalúo (Q)"
                  type="number"
                  {...register('appraisalValue', { valueAsNumber: true })}
                  error={errors.appraisalValue?.message}
                />
                <Select
                  label="Propietario"
                  {...register('borrowerId')}
                  error={errors.borrowerId?.message}
                  options={[
                    { value: '', label: 'Seleccionar propietario...' },
                    ...(borrowersData?.data.map(b => ({
                      value: b.id,
                      label: `${b.firstName} ${b.lastName} - ${b.dpi}`,
                    })) || []),
                  ]}
                />
              </div>
            </div>
          </Card>
        </div>

        <div className="mt-6 flex justify-end gap-4">
          <Link to={ROUTES.PROPERTIES}>
            <Button variant="outline" type="button">
              Cancelar
            </Button>
          </Link>
          <Button type="submit" disabled={isSubmitting}>
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Guardando...' : isEditing ? 'Actualizar' : 'Crear Propiedad'}
          </Button>
        </div>
      </form>
    </PageLayout>
  );
}
