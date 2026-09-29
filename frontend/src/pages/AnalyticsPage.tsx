import { useQuery } from '@tanstack/react-query'
import { getCharts } from '@/api/dashboard'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { formatCurrency } from '@/utils/formatters'

const COLORS = ['#6366f1', '#8b5cf6', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']

export function AnalyticsPage() {
  const { data: charts, isLoading } = useQuery({
    queryKey: ['dashboard-charts'],
    queryFn: getCharts,
  })

  if (isLoading) return <LoadingSpinner />
  if (!charts) return null

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Leads over time */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Leads Over Time</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={charts.leads_over_time}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="leads" stroke="#6366f1" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Revenue by month */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Revenue by Month</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={charts.revenue_by_month}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v: number) => formatCurrency(v)} />
              <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pipeline by stage */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Pipeline by Stage</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={charts.pipeline_by_stage} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 12 }} tickFormatter={(v) => `$${(v/1000).toFixed(0)}k`} />
              <YAxis dataKey="stage" type="category" tick={{ fontSize: 12 }} width={80} />
              <Tooltip formatter={(v: number) => formatCurrency(v)} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {charts.pipeline_by_stage.map((entry: any, i: number) => (
                  <Cell key={i} fill={entry.color || COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Lead sources */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Lead Sources</h2>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={charts.lead_sources}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="count"
                  nameKey="source"
                  label={({ source, percent }) => `${source} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {charts.lead_sources.map((_: any, i: number) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Rep performance table */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Sales Rep Performance</h2>
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-gray-200">
              {['Representative', 'Leads Owned', 'Deals Won', 'Revenue Generated'].map(h => (
                <th key={h} className="py-3 pr-6 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {charts.rep_performance.map((rep: any) => (
              <tr key={rep.name} className="hover:bg-gray-50">
                <td className="py-3 pr-6 font-medium text-gray-900">{rep.name}</td>
                <td className="py-3 pr-6 text-gray-600">{rep.leads}</td>
                <td className="py-3 pr-6 text-gray-600">{rep.won_deals}</td>
                <td className="py-3 pr-6 font-semibold text-green-600">{formatCurrency(rep.revenue)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
