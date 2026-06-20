import { cn } from '../../utils/cn';

function getGradeStyle(grade: string | null): string {
  switch (grade) {
    case 'A': return 'bg-green-100  text-green-800  border-green-200';
    case 'B': return 'bg-blue-100   text-blue-800   border-blue-200';
    case 'C': return 'bg-amber-100  text-amber-800  border-amber-200';
    case 'D': return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'F': return 'bg-red-100    text-red-800    border-red-200';
    default:  return 'bg-gray-100   text-gray-600   border-gray-200';
  }
}

interface TrustScoreBadgeProps {
  score: number | null;
  grade: string | null;
  size?: 'sm' | 'lg';
}

export function TrustScoreBadge({ score, grade, size = 'sm' }: TrustScoreBadgeProps) {
  if (score === null) {
    return (
      <span className="text-xs text-ink-hint">Not analyzed</span>
    );
  }

  if (size === 'lg') {
    return (
      <div className={cn(
        'flex flex-col items-center justify-center rounded-2xl border-2 p-4',
        getGradeStyle(grade)
      )}>
        <span className="text-4xl font-bold">{grade ?? '?'}</span>
        <span className="text-sm font-medium mt-1">{score.toFixed(1)} / 100</span>
        <span className="text-xs mt-0.5">Trust Score</span>
      </div>
    );
  }

  return (
    <span className={cn(
      'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium border',
      getGradeStyle(grade)
    )}>
      <span className="font-bold">{grade ?? '?'}</span>
      <span>{score.toFixed(0)}</span>
    </span>
  );
}