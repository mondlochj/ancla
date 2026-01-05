import * as React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthLayout } from '@/components/layout';
import { Button, Input, Alert } from '@/components/ui';
import { useAuthStore } from '@/store/authStore';
import { ROUTES } from '@/lib/constants';
import type { LoginCredentials } from '@/types';

const loginSchema = z.object({
  email: z.string().email('Correo electrónico inválido'),
  password: z.string().min(1, 'La contraseña es requerida'),
  rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading } = useAuthStore();
  const [error, setError] = React.useState<string | null>(null);

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || ROUTES.DASHBOARD;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setError(null);
    try {
      await login(data as LoginCredentials);
      navigate(from, { replace: true });
    } catch (err) {
      setError(
        (err as { message?: string })?.message ||
        'Credenciales inválidas. Por favor intente de nuevo.'
      );
    }
  };

  return (
    <AuthLayout
      title="Iniciar Sesión"
      subtitle="Ingrese sus credenciales para acceder"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {error && (
          <Alert variant="danger" dismissible onDismiss={() => setError(null)}>
            {error}
          </Alert>
        )}

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
          error={errors.password?.message}
          {...register('password')}
        />

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-sm text-gray-600">
            <input
              type="checkbox"
              className="rounded border-gray-300"
              {...register('rememberMe')}
            />
            Recordarme
          </label>
          <Link
            to={ROUTES.FORGOT_PASSWORD}
            className="text-sm text-secondary hover:underline"
          >
            ¿Olvidó su contraseña?
          </Link>
        </div>

        <Button
          type="submit"
          className="w-full"
          isLoading={isLoading}
        >
          Iniciar Sesión
        </Button>

        <p className="text-center text-sm text-gray-600">
          ¿No tiene cuenta?{' '}
          <Link to={ROUTES.REGISTER} className="text-secondary hover:underline">
            Registrarse
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}

export default Login;
