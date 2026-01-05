import * as React from 'react';
import { cn } from '@/lib/utils';

export interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  className?: string;
}

export function AuthLayout({
  children,
  title,
  subtitle,
  className,
}: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4">
      <div
        className={cn(
          'w-full max-w-md bg-white rounded-lg shadow-lg p-10',
          className
        )}
      >
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <img
            src="/logo.png"
            alt="Ancla Capital"
            className="h-16 mx-auto mb-4"
          />
          <h1 className="text-2xl font-semibold text-primary">{title}</h1>
          {subtitle && (
            <p className="mt-2 text-sm text-gray-500">{subtitle}</p>
          )}
        </div>

        {children}
      </div>
    </div>
  );
}

export default AuthLayout;
