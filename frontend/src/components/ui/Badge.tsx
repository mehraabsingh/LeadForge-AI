import { clsx } from 'clsx';
import {
  LEAD_STATUS_COLORS,
  LEAD_PRIORITY_COLORS,
  TASK_STATUS_COLORS,
  OPPORTUNITY_STATUS_COLORS,
} from '../../utils/constants';

type BadgeVariant = 'gray' | 'blue' | 'green' | 'yellow' | 'red' | 'orange' | 'purple' | 'indigo';

const VARIANT_COLORS: Record<BadgeVariant, string> = {
  gray: 'bg-gray-100 text-gray-700',
  blue: 'bg-blue-100 text-blue-800',
  green: 'bg-green-100 text-green-800',
  yellow: 'bg-yellow-100 text-yellow-800',
  red: 'bg-red-100 text-red-800',
  orange: 'bg-orange-100 text-orange-800',
  purple: 'bg-purple-100 text-purple-800',
  indigo: 'bg-indigo-100 text-indigo-800',
};

interface BadgeProps {
  label?: string;
  children?: React.ReactNode;
  colorClass?: string;
  variant?: BadgeVariant;
  /** Auto-detect color from known status/priority maps */
  status?: string;
  className?: string;
  size?: 'sm' | 'md';
}

function resolveColor(status: string): string {
  const all: Record<string, string> = {
    ...LEAD_STATUS_COLORS,
    ...LEAD_PRIORITY_COLORS,
    ...TASK_STATUS_COLORS,
    ...OPPORTUNITY_STATUS_COLORS,
  };
  return all[status] ?? 'bg-gray-100 text-gray-700';
}

import React from 'react';

export function Badge({ label, children, colorClass, variant, status, className, size = 'md' }: BadgeProps) {
  const color = colorClass 
    ?? (variant ? VARIANT_COLORS[variant] : undefined)
    ?? (status ? resolveColor(status) : 'bg-gray-100 text-gray-700');

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full font-medium',
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-0.5 text-xs',
        color,
        className,
      )}
    >
      {children ?? label}
    </span>
  );
}
