import { cn } from '../../utils/cn';
import type { ClaimStatus } from '../../types/claim';

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple' | ClaimStatus;

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const variantStyles: Record<string, string> = {
  default:          'bg-gray-100 text-gray-700',
  success:          'bg-green-100 text-green-800',
  warning:          'bg-orange-100 text-orange-800',
  danger:           'bg-red-100 text-red-800',
  info:             'bg-blue-100 text-blue-800',
  purple:           'bg-purple-100 text-purple-800',
  draft:            'bg-gray-100 text-gray-700',
  submitted:        'bg-blue-100 text-blue-800',
  under_review:     'bg-orange-100 text-orange-800',
  approved:         'bg-green-100 text-green-800',
  rejected:         'bg-red-100 text-red-800',
  needs_inspection: 'bg-purple-100 text-purple-800',
};

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        variantStyles[variant] ?? variantStyles.default,
        className
      )}
    >
      {children}
    </span>
  );
}