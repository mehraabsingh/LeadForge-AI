import { useQuery } from '@tanstack/react-query';
import {
  Users, TrendingUp, DollarSign, Target, Award, BarChart2
} from 'lucide-react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { getStats, getCharts } from '@/api/dashboard';
import { getSalesInsights } from '@/api/ai';
import { StatCard } from '@/components/ui/StatCard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { formatCurrency } from '@/utils/formatters';
import { CHART_COLORS } from '@/utils/constants';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';
import clsx from 'clsx';

const SEVERITY_BADGE: Record<string, string> = {
  critical: 'bg-red-50 border-red-200 text-red-700',
  high: 'bg-orange-50 border-orange-200 text-orange-700',
  medium: 'bg-yellow-50 border-yellow-200 text-yellow-700',
  low: 'bg-blue-50 border-blue-200 text-blue-700',
};

export function DashboardPage() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: getStats,
  });

  const { data: charts, isLoading: chartsLoading } = useQuery({
    queryKey: ['dashboard', 'charts'],
    queryFn: getCharts,
  });

  const { data: insightsData } = useQuery({
    queryKey: ['ai', 'insights'],
    queryFn: getSalesInsights,
    staleTime: 1000 * 60 * 5,
  });

  const insights = insightsData?.insights ?? [];

  if (statsLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Your sales pipeline at a glance</p>
      </div>

      {/* KPI Cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Total Leads"
            value={stats.total_leads}
            icon={<Users className="h-5 w-5" />}
            colorClass="bg-indigo-50 text-indigo-600"
          />
          <StatCard
            label="Qualified Leads"
            value={stats.qualified_leads}
            icon={<Target className="h-5 w-5" />}
            colorClass="bg-green-50 text-green-600"
          />
          <StatCard
            label="Open Opportunities"
            value={stats.open_opportunities}
            icon={<TrendingUp className="h-5 w-5" />}
            colorClass="bg-blue-50 text-blue-600"
          />
          <StatCard
            label="Pipeline Value"
            value={formatCurrency(stats.pipeline_value)}
            icon={<DollarSign className="h-5 w-5" />}
            colorClass="bg-purple-50 text-purple-600"
          />
          <StatCard
            label="Weighted Pipeline"
            value={formatCurrency(stats.weighted_pipeline)}
            icon={<BarChart2 className="h-5 w-5" />}
            colorClass="bg-indigo-50 text-indigo-600"
          />
          <StatCard
            label="Won Revenue"
            value={formatCurrency(stats.won_revenue)}
            icon={<Award className="h-5 w-5" />}
            colorClass="bg-green-50 text-green-600"
          />
          <StatCard
            label="Win Rate"
            value={`${stats.win_rate}%`}
            icon={<Target className="h-5 w-5" />}
            colorClass="bg-blue-50 text-blue-600"
          />
          <StatCard
            label="Conversion Rate"
            value={`${stats.conversion_rate}%`}
            icon={<TrendingUp className="h-5 w-5" />}
            colorClass="bg-purple-50 text-purple-600"
          />
        </div>
      )}

      {/* Charts */}
      {chartsLoading ? (
        <LoadingSpinner />
      ) : charts ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Leads over time */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4">Leads Over Time</h2>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={charts.leads_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="leads" stroke="#6366f1" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Revenue by month */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4">Revenue by Month</h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={charts.revenue_by_month}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="month" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(v: number) => formatCurrency(v)} />
                <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Lead sources */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4">Lead Sources</h2>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={charts.lead_sources} cx="50%" cy="50%" outerRadius={80} dataKey="count" nameKey="source">
                  {charts.lead_sources.map((_: unknown, i: number) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex flex-wrap gap-2 mt-2 justify-center">
              {charts.lead_sources.map((s: { source: string }, i: number) => (
                <div key={s.source} className="flex items-center gap-1 text-xs text-gray-500">
                  <span className="h-2 w-2 rounded-full" style={{ backgroundColor: CHART_COLORS[i % CHART_COLORS.length] }} />
                  {s.source}
                </div>
              ))}
            </div>
          </div>

          {/* Rep performance */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold text-gray-900 mb-4">Rep Performance</h2>
            <div className="space-y-2">
              {charts.rep_performance.map((rep: { name: string; leads: number; won_deals: number; revenue: number }) => (
                <div key={rep.name} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div className="flex-1">
                    <p className="font-medium text-sm text-gray-900">{rep.name}</p>
                    <p className="text-xs text-gray-400">{rep.leads} leads · {rep.won_deals} won</p>
                  </div>
                  <span className="text-sm font-semibold text-green-600">{formatCurrency(rep.revenue)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}

      {/* AI Insights Preview */}
      {insights.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-900">AI Sales Insights</h2>
            <a href="/ai-insights" className="text-sm text-indigo-600 hover:underline">View all →</a>
          </div>
          <div className="space-y-3">
            {insights.slice(0, 3).map((insight, idx) => (
              <div key={idx} className={clsx('rounded-lg border p-4', SEVERITY_BADGE[insight.severity] || SEVERITY_BADGE.low)}>
                <div className="flex items-start gap-3">
                  {insight.severity === 'critical' || insight.severity === 'high'
                    ? <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    : insight.severity === 'medium'
                    ? <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    : <Info className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  }
                  <div>
                    <p className="font-medium text-sm">{insight.title}</p>
                    <p className="text-xs mt-0.5 opacity-80">{insight.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
