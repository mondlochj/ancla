import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Edit, MapPin, CheckCircle, XCircle } from 'lucide-react';
import { PageLayout, PageHeader } from '@/components/layout';
import { Card, Button, Spinner, Alert } from '@/components/ui';
import { StatusBadge } from '@/components/data';
import { propertiesService } from '@/services';
import { formatDate, formatCurrency } from '@/lib/utils';
import { ROUTES } from '@/lib/constants';
import { useAuthStore } from '@/store/authStore';

export default function PropertyDetail() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  const { data: property, isLoading } = useQuery({
    queryKey: ['property', id],
    queryFn: () => propertiesService.getProperty(id!),
    enabled: !!id,
  });

  const verifyMutation = useMutation({
    mutationFn: (status: 'Verified' | 'Rejected') => propertiesService.verifyProperty(id!, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['property', id] });
      queryClient.invalidateQueries({ queryKey: ['properties'] });
    },
  });

  if (isLoading) {
    return (
      <PageLayout>
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      </PageLayout>
    );
  }

  if (!property) {
    return (
      <PageLayout>
        <div className="text-center py-12">
          <p className="text-gray-500">Propiedad no encontrada</p>
          <Link to={ROUTES.PROPERTIES}>
            <Button variant="outline" className="mt-4">
              Volver a la lista
            </Button>
          </Link>
        </div>
      </PageLayout>
    );
  }

  const canVerify = user?.role === 'Admin' && property.verificationStatus === 'Pending';

  return (
    <PageLayout>
      <div className="mb-6">
        <Link to={ROUTES.PROPERTIES} className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Volver a propiedades
        </Link>
      </div>

      <PageHeader
        title={`Propiedad ${property.registryNumber}`}
        description={property.propertyType}
        action={
          <div className="flex gap-2">
            {canVerify && (
              <>
                <Button
                  variant="outline"
                  className="text-red-600 border-red-600 hover:bg-red-50"
                  onClick={() => verifyMutation.mutate('Rejected')}
                  disabled={verifyMutation.isPending}
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Rechazar
                </Button>
                <Button
                  className="bg-green-600 hover:bg-green-700"
                  onClick={() => verifyMutation.mutate('Verified')}
                  disabled={verifyMutation.isPending}
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Verificar
                </Button>
              </>
            )}
            <Link to={ROUTES.PROPERTY_EDIT(property.id)}>
              <Button variant="outline">
                <Edit className="h-4 w-4 mr-2" />
                Editar
              </Button>
            </Link>
          </div>
        }
      />

      {verifyMutation.isError && (
        <Alert variant="error" className="mb-6">
          Error al verificar la propiedad
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información de Registro</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-500">Número de Registro</label>
                  <p className="font-medium">{property.registryNumber}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Finca</label>
                  <p className="font-medium">{property.finca || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Folio</label>
                  <p className="font-medium">{property.folio || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Libro</label>
                  <p className="font-medium">{property.libro || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Tipo de Propiedad</label>
                  <p className="font-medium">{property.propertyType}</p>
                </div>
                <div>
                  <label className="text-sm text-gray-500">Estado de Verificación</label>
                  <div className="mt-1">
                    <StatusBadge status={property.verificationStatus} type="verification" />
                  </div>
                </div>
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Ubicación</h3>
              <div className="flex items-start gap-3 mb-4">
                <MapPin className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="font-medium">{property.address}</p>
                  <p className="text-gray-500">{property.municipality}, {property.department}</p>
                </div>
              </div>
              {property.latitude && property.longitude && (
                <div className="bg-gray-100 rounded-lg h-48 flex items-center justify-center">
                  <p className="text-gray-500">Mapa: {property.latitude}, {property.longitude}</p>
                </div>
              )}
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Características</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm text-gray-500">Área Total</label>
                  <p className="font-medium">{property.area?.toLocaleString()} m²</p>
                </div>
                {property.constructionArea && (
                  <div>
                    <label className="text-sm text-gray-500">Área de Construcción</label>
                    <p className="font-medium">{property.constructionArea.toLocaleString()} m²</p>
                  </div>
                )}
                {property.bedrooms && (
                  <div>
                    <label className="text-sm text-gray-500">Habitaciones</label>
                    <p className="font-medium">{property.bedrooms}</p>
                  </div>
                )}
                {property.bathrooms && (
                  <div>
                    <label className="text-sm text-gray-500">Baños</label>
                    <p className="font-medium">{property.bathrooms}</p>
                  </div>
                )}
                {property.parkingSpaces && (
                  <div>
                    <label className="text-sm text-gray-500">Parqueos</label>
                    <p className="font-medium">{property.parkingSpaces}</p>
                  </div>
                )}
                {property.yearBuilt && (
                  <div>
                    <label className="text-sm text-gray-500">Año de Construcción</label>
                    <p className="font-medium">{property.yearBuilt}</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Valuación</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-gray-500">Valor Estimado</label>
                  <p className="text-2xl font-bold text-primary">
                    {formatCurrency(property.estimatedValue)}
                  </p>
                </div>
                {property.lastAppraisalDate && (
                  <div>
                    <label className="text-sm text-gray-500">Última Valuación</label>
                    <p className="font-medium">{formatDate(property.lastAppraisalDate)}</p>
                  </div>
                )}
                {property.appraisalValue && (
                  <div>
                    <label className="text-sm text-gray-500">Valor de Avalúo</label>
                    <p className="font-medium">{formatCurrency(property.appraisalValue)}</p>
                  </div>
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Propietario</h3>
              {property.borrower ? (
                <div>
                  <Link
                    to={ROUTES.BORROWER_DETAIL(property.borrower.id)}
                    className="text-blue-600 hover:underline font-medium"
                  >
                    {property.borrower.firstName} {property.borrower.lastName}
                  </Link>
                  <p className="text-sm text-gray-500 mt-1">{property.borrower.dpi}</p>
                </div>
              ) : (
                <p className="text-gray-500">Sin propietario asignado</p>
              )}
            </div>
          </Card>

          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Información del Sistema</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <label className="text-gray-500">Fecha de Registro</label>
                  <p>{formatDate(property.createdAt)}</p>
                </div>
                <div>
                  <label className="text-gray-500">Última Actualización</label>
                  <p>{formatDate(property.updatedAt)}</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </PageLayout>
  );
}
