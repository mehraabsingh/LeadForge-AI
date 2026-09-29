import React from 'react';
import { clsx } from 'clsx';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number; // percent change, positive = up
  trendLabel?: string;
  colorClass?: string;
  className?: string;
}

export function StatCard({
  label,
  value,
  icon,
  trend,
  trendLabel,
  colorClass = 'bg-indigo-50 text-indigo-600',
  className,
}: StatCardProps) {
  const isPositive = trend !== undefined && trend > 0;
  const isNegative = trend !== undefined && trend < 0;
  const isNeutral = trend !== undefined && trend === 0;

  return (
    <div
      className={clsx(
        'bg-white rounded-xl border border-gray-200 shadow-sm p-6',
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="mt-1.5 text-2xl font-bold text-gray-900 tracking-tight">
            {value}
          </p>
        </div>
        <div className={clsx('h-10 w-10 rounded-xl flex items-center justify-center', colorClass)}>
          {icon}
        </div>
      </div>

      {trend !== undefined && (
        <div className="mt-4 flex items-center gap-1.5">
          {isPositive && <TrendingUp className="h-4 w-4 text-green-500" />}
          {isNegative && <TrendingDown className="h-4 w-4 text-red-500" />}
          {isNeutral && <Minus className="h-4 w-4 text-gray-400" />}
          <span
            className={clsx(
              'text-sm font-medium',
              isPositive && 'text-green-600',
              isNegative && 'text-red-600',
              isNeutral && 'text-gray-500',
            )}
          >
            {isPositive ? '+' : ''}
            {trend.toFixed(1)}%
          </span>
          {trendLabel && (
            <span className="text-xs text-gray-400">{trendLabel}</span>
          )}
        </div>
      )}
    </div>
  );
}
