import * as React from 'react';
import { cn, formatCurrency } from '@/lib/utils';

export interface CurrencyProps extends React.HTMLAttributes<HTMLSpanElement> {
  amount: number;
  showSign?: boolean;
  colorCode?: boolean;
}

export const Currency = React.forwardRef<HTMLSpanElement, CurrencyProps>(
  ({ amount, showSign = false, colorCode = false, className, ...props }, ref) => {
    const formatted = formatCurrency(Math.abs(amount));
    const displayValue = showSign && amount > 0 ? `+${formatted}` : amount < 0 ? `-${formatted}` : formatted;

    return (
      <span
        ref={ref}
        className={cn(
          'tabular-nums',
          colorCode && amount > 0 && 'text-success',
          colorCode && amount < 0 && 'text-danger',
          className
        )}
        {...props}
      >
        {displayValue}
      </span>
    );
  }
);

Currency.displayName = 'Currency';

export default Currency;
