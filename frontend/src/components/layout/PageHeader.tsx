import * as React from 'react';
import { cn } from '@/lib/utils';

export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  description?: string;
  actions?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export function PageHeader({
  title,
  subtitle,
  description,
  actions,
  action,
  className,
}: PageHeaderProps) {
  const descText = description || subtitle;
  const actionContent = action || actions;

  return (
    <div
      className={cn(
        'flex items-center justify-between mb-6',
        className
      )}
    >
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
        {descText && (
          <p className="mt-1 text-sm text-gray-500">{descText}</p>
        )}
      </div>
      {actionContent && (
        <div className="flex items-center gap-2">{actionContent}</div>
      )}
    </div>
  );
}

export default PageHeader;
