import { clsx } from 'clsx';
import { getScoreColor, getScoreLabel } from '../../utils/formatters';

interface ScoreBadgeProps {
  score?: number;
  label?: string;
  size?: 'sm' | 'md';
  className?: string;
}

export function ScoreBadge({ score, label, size = 'md', className }: ScoreBadgeProps) {
  if (score === undefined && !label) {
    return (
      <span className="text-xs text-gray-400 italic">Not scored</span>
    );
  }

  const colorClass = getScoreColor(score);
  const displayLabel = label ?? getScoreLabel(score);

  return (
    <div className={clsx('inline-flex items-center gap-1.5 rounded-full', colorClass,
      size === 'sm' ? 'px-2 py-0.5' : 'px-3 py-1',
      className
    )}>
      {score !== undefined && (
        <span className={clsx('font-bold', size === 'sm' ? 'text-xs' : 'text-sm')}>
          {score}
        </span>
      )}
      <span className={clsx('font-semibold uppercase tracking-wide', size === 'sm' ? 'text-xs' : 'text-xs')}>
        {displayLabel}
      </span>
    </div>
  );
}
