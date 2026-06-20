import { cn } from '../../utils/cn';

interface FraudScoreBarProps {
  label: string;
  score: number;
  maxScore: number;
  flags: string[];
}

export function FraudScoreBar({ label, score, maxScore, flags }: FraudScoreBarProps) {
  const pct       = maxScore > 0 ? (score / maxScore) * 100 : 0;
  const isGood    = pct >= 70;
  const isMedium  = pct >= 40 && pct < 70;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-ink">{label}</span>
        <span className={cn(
          'font-semibold tabular-nums',
          isGood ? 'text-success' : isMedium ? 'text-warning' : 'text-danger'
        )}>
          {score.toFixed(1)} / {maxScore}
        </span>
      </div>
      <div className="h-2 bg-border rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500',
            isGood ? 'bg-success' : isMedium ? 'bg-warning' : 'bg-danger'
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
      {flags.length > 0 && (
        <ul className="space-y-0.5">
          {flags.map((flag, i) => (
            <li key={i} className="text-xs text-danger flex items-start gap-1">
              <span className="mt-0.5 flex-shrink-0">⚠</span>
              <span>{flag}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}