import { useQuery } from '@tanstack/react-query'
import { getSalesInsights } from '@/api/ai'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Brain, AlertTriangle, TrendingUp, Info, RefreshCw } from 'lucide-react'
import clsx from 'clsx'

const SEVERITY_CONFIG: Record<string, { color: string; bg: string; icon: typeof AlertTriangle }> = {
  critical: { color: 'text-red-700', bg: 'bg-red-50 border-red-200', icon: AlertTriangle },
  high: { color: 'text-orange-700', bg: 'bg-orange-50 border-orange-200', icon: AlertTriangle },
  medium: { color: 'text-yellow-700', bg: 'bg-yellow-50 border-yellow-200', icon: Info },
  low: { color: 'text-blue-700', bg: 'bg-blue-50 border-blue-200', icon: Info },
}

export function AIInsightsPage() {
  const { data: insights, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['ai-insights'],
    queryFn: getSalesInsights,
    staleTime: 0, // Always fresh
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-indigo-100 flex items-center justify-center">
            <Brain className="h-6 w-6 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Sales Insights</h1>
            <p className="text-sm text-gray-500">Based on real pipeline data • Fallback engine active</p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={clsx('h-4 w-4', isFetching && 'animate-spin')} />
          Refresh
        </button>
      </div>

      {isLoading ? (
        <LoadingSpinner />
      ) : !insights?.insights?.length ? (
        <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
          <TrendingUp className="h-12 w-12 text-green-500 mx-auto mb-3" />
          <h3 className="font-semibold text-green-700">Pipeline Looking Healthy!</h3>
          <p className="text-green-600 text-sm mt-1">No critical issues detected in your current pipeline.</p>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            {insights.total_insights} insight{insights.total_insights !== 1 ? 's' : ''} generated
            {insights.generated_at ? ` • ${new Date(insights.generated_at).toLocaleTimeString()}` : ''}
          </p>

          {/* Critical first */}
          {['critical', 'high', 'medium', 'low'].map(severity => {
            const sevInsights = insights.insights.filter(i => i.severity === severity)
            if (!sevInsights.length) return null

            return sevInsights.map(insight => {
              const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.low
              const IconComp = config.icon

              return (
                <div
                  key={insight.title}
                  className={clsx('rounded-xl border p-5', config.bg)}
                >
                  <div className="flex items-start gap-4">
                    <div className={clsx('mt-0.5 flex-shrink-0', config.color)}>
                      <IconComp className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className={clsx('font-semibold', config.color)}>{insight.title}</h3>
                        <span className={clsx(
                          'text-xs px-2 py-0.5 rounded-full font-medium uppercase',
                          config.color,
                          config.bg
                        )}>
                          {severity}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mt-1">{insight.description}</p>
                      <div className="mt-3 bg-white/60 rounded-lg p-3">
                        <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Recommended Action</p>
                        <p className="text-sm text-gray-700">{insight.action}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })
          })}
        </div>
      )}
    </div>
  )
}
