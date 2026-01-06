import * as React from 'react';
import { cn } from '@/lib/utils';
import { X, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'error';
  title?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

const variantStyles = {
  success: 'bg-success-light text-success-dark border-green-300',
  warning: 'bg-warning-light text-warning-dark border-amber-300',
  danger: 'bg-danger-light text-danger-dark border-red-300',
  error: 'bg-danger-light text-danger-dark border-red-300',
  info: 'bg-info-light text-info-dark border-sky-300',
};

const iconMap = {
  success: CheckCircle,
  warning: AlertTriangle,
  danger: XCircle,
  error: XCircle,
  info: Info,
};

export const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = 'info', title, dismissible = false, onDismiss, children, ...props }, ref) => {
    const Icon = iconMap[variant];

    return (
      <div
        ref={ref}
        role="alert"
        className={cn(
          'flex items-start gap-3 p-4 rounded-md border',
          variantStyles[variant],
          className
        )}
        {...props}
      >
        <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          {title && (
            <h5 className="font-medium mb-1">{title}</h5>
          )}
          <div className="text-sm">{children}</div>
        </div>
        {dismissible && (
          <button
            type="button"
            onClick={onDismiss}
            className="flex-shrink-0 p-1 rounded hover:bg-black/5 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    );
  }
);

Alert.displayName = 'Alert';

export default Alert;
