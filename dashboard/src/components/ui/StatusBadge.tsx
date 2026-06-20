import { cn } from '../../utils/cn';

const STATUS_STYLES: Record<string, string> = {
  submitted:        'bg-blue-100   text-blue-800',
  under_review:     'bg-amber-100  text-amber-800',
  approved:         'bg-green-100  text-green-800',
  rejected:         'bg-red-100    text-red-800',
  needs_inspection: 'bg-purple-100 text-purple-800',
  draft:            'bg-gray-100   text-gray-700',
};

const STATUS_LABELS: Record<string, string> = {
  submitted:        'Submitted',
  under_review:     'Under Review',
  approved:         'Approved',
  rejected:         'Rejected',
  needs_inspection: 'Needs Inspection',
  draft:            'Draft',
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={cn(
      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
      STATUS_STYLES[status] ?? 'bg-gray-100 text-gray-700'
    )}>
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}