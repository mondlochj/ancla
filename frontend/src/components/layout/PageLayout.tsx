import * as React from 'react';
import { cn } from '@/lib/utils';
import { Navbar } from './Navbar';

export interface PageLayoutProps {
  children: React.ReactNode;
  className?: string;
  fullWidth?: boolean;
}

export function PageLayout({
  children,
  className,
  fullWidth = false,
}: PageLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />
      <main
        className={cn(
          'py-6',
          !fullWidth && 'max-w-7xl mx-auto px-5',
          className
        )}
      >
        {children}
      </main>
      <footer className="bg-white border-t border-gray-200 py-4 text-center text-xs text-gray-500">
        &copy; {new Date().getFullYear()} Ancla Capital, S.A. - Guatemala
      </footer>
    </div>
  );
}

export default PageLayout;
