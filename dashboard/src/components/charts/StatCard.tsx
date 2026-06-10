import { cn } from '../../utils/cn';
import { Skeleton } from '../ui/Skeleton';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: { value: number; label: string };
  color?: 'green' | 'blue' | 'orange' | 'red';
  isLoading?: boolean;
}

const colors = {
  green:  { bg: 'bg-green-50',  icon: 'bg-green-100 text-green-700',  text: 'text-green-700' },
  blue:   { bg: 'bg-blue-50',   icon: 'bg-blue-100 text-blue-700',    text: 'text-blue-700' },
  orange: { bg: 'bg-orange-50', icon: 'bg-orange-100 text-orange-700', text: 'text-orange-700' },
  red:    { bg: 'bg-red-50',    icon: 'bg-red-100 text-red-700',      text: 'text-red-700' },
};

export function StatCard({
  title, value, subtitle, icon, trend, color = 'green', isLoading = false,
}: StatCardProps) {
  const c = colors[color];

  if (isLoading) return <Skeleton className="h-28 rounded-card" />;

  return (
    <div className={cn('card p-5', c.bg)}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-ink-secondary truncate">{title}</p>
          <p className="mt-1 text-2xl font-bold text-ink">{value}</p>
          {subtitle && (
            <p className="mt-0.5 text-xs text-ink-hint truncate">{subtitle}</p>
          )}
          {trend && (
            <p className={cn('mt-1 text-xs font-medium', trend.value >= 0 ? 'text-success' : 'text-danger')}>
              {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
            </p>
          )}
        </div>
        <div className={cn('flex-shrink-0 p-2.5 rounded-xl ml-3', c.icon)}>
          {icon}
        </div>
      </div>
    </div>
  );
}