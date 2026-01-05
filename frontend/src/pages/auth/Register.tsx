import * as React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { AuthLayout } from '@/components/layout';
import { Button, Input, Alert } from '@/components/ui';
import { useAuthStore } from '@/store/authStore';
import { ROUTES } from '@/lib/constants';

const registerSchema = z.object({
  email: z.string().email('Correo electrónico inválido'),
  fullName: z.string().min(2, 'El nombre debe tener al menos 2 caracteres'),
  password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Las contraseñas no coinciden',
  path: ['confirmPassword'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export function Register() {
  const navigate = useNavigate();
  const { register: registerUser, isLoading } = useAuthStore();
  const [error, setError] = React.useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    setError(null);
    try {
      await registerUser(data);
      navigate(ROUTES.DASHBOARD, { replace: true });
    } catch (err) {
      setError(
        (err as { message?: string })?.message ||
        'Error al registrar. Por favor intente de nuevo.'
      );
    }
  };

  return (
    <AuthLayout
      title="Crear Cuenta"
      subtitle="Complete el formulario para registrarse"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {error && (
          <Alert variant="danger" dismissible onDismiss={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Input
          label="Nombre Completo"
          placeholder="Juan Pérez"
          error={errors.fullName?.message}
          {...register('fullName')}
        />

        <Input
          label="Correo Electrónico"
          type="email"
          placeholder="correo@ejemplo.com"
          error={errors.email?.message}
          {...register('email')}
        />

        <Input
          label="Contraseña"
          type="password"
          placeholder="••••••••"
          helperText="Mínimo 8 caracteres"
          error={errors.password?.message}
          {...register('password')}
        />

        <Input
          label="Confirmar Contraseña"
          type="password"
          placeholder="••••••••"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />

        <Button
          type="submit"
          className="w-full"
          isLoading={isLoading}
        >
          Registrarse
        </Button>

        <p className="text-center text-sm text-gray-600">
          ¿Ya tiene cuenta?{' '}
          <Link to={ROUTES.LOGIN} className="text-secondary hover:underline">
            Iniciar Sesión
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

export default Register;
