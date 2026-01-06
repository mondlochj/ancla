import { Badge } from '@/components/ui';
import { LOAN_STATUSES, VERIFICATION_STATUSES, RISK_TIERS } from '@/lib/constants';

export interface StatusBadgeProps {
  status: string;
  type?: 'loan' | 'verification' | 'risk' | 'payment';
}

const getLabelForStatus = (status: string, type: string): string => {
  if (type === 'loan') {
    const found = LOAN_STATUSES.find(s => s.value === status);
    return found?.label || status;
  }
  if (type === 'verification') {
    const found = VERIFICATION_STATUSES.find(s => s.value === status);
    return found?.label || status;
  }
  if (type === 'risk') {
    const found = RISK_TIERS.find(s => s.value === status);
    return found?.label || status;
  }
  if (type === 'payment') {
    const paymentLabels: Record<string, string> = {
      Pending: 'Pendiente',
      Paid: 'Pagado',
      Partial: 'Parcial',
      Overdue: 'Vencido',
    };
    return paymentLabels[status] || status;
  }
  return status;
};

export function StatusBadge({ status, type = 'loan' }: StatusBadgeProps) {
  const label = getLabelForStatus(status, type);

  return (
    <Badge variant="status" status={status}>
      {label}
    </Badge>
  );
}

export default StatusBadge;
