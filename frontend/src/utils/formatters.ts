import { format, formatDistanceToNow, isValid, parseISO } from 'date-fns';
import {
  LEAD_STATUS_COLORS,
  LEAD_PRIORITY_COLORS,
  TASK_STATUS_COLORS,
  OPPORTUNITY_STATUS_COLORS,
} from './constants';
import { LeadStatus, LeadPriority, TaskStatus, OpportunityStatus } from '../types';

// ─── Currency ──────────────────────────────────────────────────────────────────

export function formatCurrency(value: number | undefined | null, currency = 'USD'): string {
  if (value === undefined || value === null) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}

// ─── Dates ─────────────────────────────────────────────────────────────────────

export function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return '—';
  const d = parseISO(dateStr);
  if (!isValid(d)) return '—';
  return format(d, 'MMM d, yyyy');
}

export function formatDateTime(dateStr: string | undefined | null): string {
  if (!dateStr) return '—';
  const d = parseISO(dateStr);
  if (!isValid(d)) return '—';
  return format(d, 'MMM d, yyyy h:mm a');
}

export function formatRelativeDate(dateStr: string | undefined | null): string {
  if (!dateStr) return '—';
  const d = parseISO(dateStr);
  if (!isValid(d)) return '—';
  return formatDistanceToNow(d, { addSuffix: true });
}

// ─── Status / Priority Colors ─────────────────────────────────────────────────

export function getStatusColor(status: string): string {
  return LEAD_STATUS_COLORS[status as LeadStatus] ?? 'bg-gray-100 text-gray-800';
}

export function getPriorityColor(priority: string): string {
  return LEAD_PRIORITY_COLORS[priority as LeadPriority] ?? 'bg-gray-100 text-gray-800';
}

export function getTaskStatusColor(status: string): string {
  return TASK_STATUS_COLORS[status as TaskStatus] ?? 'bg-gray-100 text-gray-800';
}

export function getOpportunityStatusColor(status: string): string {
  return OPPORTUNITY_STATUS_COLORS[status as OpportunityStatus] ?? 'bg-gray-100 text-gray-800';
}

// ─── Score ─────────────────────────────────────────────────────────────────────

export function getScoreColor(score: number | undefined): string {
  if (score === undefined) return 'bg-gray-100 text-gray-500';
  if (score >= 70) return 'bg-red-100 text-red-700'; // HOT
  if (score >= 40) return 'bg-yellow-100 text-yellow-700'; // WARM
  return 'bg-blue-100 text-blue-700'; // COLD
}

export function getScoreLabel(score: number | undefined): string {
  if (score === undefined) return 'N/A';
  if (score >= 70) return 'HOT';
  if (score >= 40) return 'WARM';
  return 'COLD';
}

// ─── Numbers ───────────────────────────────────────────────────────────────────

export function formatNumber(value: number | undefined | null): string {
  if (value === undefined || value === null) return '—';
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatPercent(value: number | undefined | null): string {
  if (value === undefined || value === null) return '—';
  return `${value.toFixed(1)}%`;
}

// ─── Truncate ──────────────────────────────────────────────────────────────────

export function truncate(str: string | undefined, maxLen = 50): string {
  if (!str) return '';
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen) + '…';
}

// ─── Initials ──────────────────────────────────────────────────────────────────

export function getInitials(name: string | undefined): string {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}
