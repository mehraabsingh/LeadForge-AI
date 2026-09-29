import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getOpportunities, updateOpportunity } from '@/api/opportunities'
import { getPipelines } from '@/api/pipelines'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { formatCurrency } from '@/utils/formatters'
import { TrendingUp, ChevronRight } from 'lucide-react'
import clsx from 'clsx'
import { PipelineStage, OpportunityStatus } from '@/types'

export function OpportunitiesPage() {
  const queryClient = useQueryClient()

  const { data: pipelinesData, isLoading: pipelineLoading } = useQuery({
    queryKey: ['pipelines'],
    queryFn: getPipelines,
  })

  const { data: oppsData, isLoading: oppsLoading } = useQuery({
    queryKey: ['opportunities'],
    queryFn: () => getOpportunities({}),
  })

  const moveStage = useMutation({
    mutationFn: ({ id, stage_id }: { id: string; stage_id: string }) =>
      updateOpportunity(id, { stage_id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['opportunities'] })
      queryClient.invalidateQueries({ queryKey: ['pipelines'] })
    },
  })

  if (pipelineLoading || oppsLoading) return <LoadingSpinner />

  const pipeline = pipelinesData?.[0]
  const opps = oppsData?.opportunities || []
  const openStages = pipeline?.stages?.filter(s => s.name !== 'Won' && s.name !== 'Lost') || []

  const oppsByStage = (stageId: string) =>
    opps.filter(o => o.stage_id === stageId && o.status === 'OPEN')

  return (
    <div className="space-y-6">
      {/* Header with pipeline metrics */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Sales Pipeline</h1>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase font-medium">Pipeline Value</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {formatCurrency(oppsData?.pipeline_value || 0)}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase font-medium">Weighted Value</p>
          <p className="text-2xl font-bold text-indigo-600 mt-1">
            {formatCurrency(oppsData?.weighted_value || 0)}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase font-medium">Won Revenue</p>
          <p className="text-2xl font-bold text-green-600 mt-1">
            {formatCurrency(oppsData?.won_value || 0)}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs text-gray-500 uppercase font-medium">Win Rate</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {oppsData?.win_rate?.toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Kanban Board */}
      {!pipeline ? (
        <EmptyState
          icon={<TrendingUp className="h-12 w-12 text-gray-400" />}
          title="No pipeline configured"
          description="Create a pipeline to start tracking opportunities"
        />
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {openStages.map(stage => {
            const stageOpps = oppsByStage(stage.id)
            const stageValue = stageOpps.reduce((s, o) => s + (o.value || 0), 0)

            return (
              <div key={stage.id} className="flex-shrink-0 w-72">
                {/* Stage Header */}
                <div className="flex items-center justify-between mb-2 px-1">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: stage.color || '#6366f1' }}
                    />
                    <span className="font-medium text-sm text-gray-700">{stage.name}</span>
                    <span className="text-xs bg-gray-100 text-gray-500 rounded-full px-2 py-0.5">
                      {stageOpps.length}
                    </span>
                  </div>
                  <span className="text-xs font-medium text-gray-500">
                    {formatCurrency(stageValue)}
                  </span>
                </div>

                {/* Cards */}
                <div className="space-y-2 min-h-[100px]">
                  {stageOpps.map(opp => (
                    <OppCard
                      key={opp.id}
                      opp={opp}
                      allStages={openStages}
                      onMove={(stage_id) => moveStage.mutate({ id: opp.id, stage_id })}
                    />
                  ))}
                  {stageOpps.length === 0 && (
                    <div className="rounded-lg border-2 border-dashed border-gray-200 h-16 flex items-center justify-center">
                      <p className="text-xs text-gray-400">No deals</p>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function OppCard({
  opp,
  allStages,
  onMove,
}: {
  opp: any
  allStages: PipelineStage[]
  onMove: (stageId: string) => void
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <p className="font-medium text-sm text-gray-900 leading-tight">{opp.title}</p>
      <p className="text-xs text-gray-500 mt-1">{opp.owner?.full_name}</p>

      <div className="mt-3 flex items-center justify-between">
        <span className="text-base font-bold text-gray-900">
          {formatCurrency(opp.value || 0)}
        </span>
        <span className="text-xs text-gray-400">{opp.probability}%</span>
      </div>

      {/* Move stage */}
      <div className="mt-3">
        <select
          className="w-full text-xs border border-gray-200 rounded-lg px-2 py-1 text-gray-600 bg-gray-50"
          value={opp.stage_id}
          onChange={(e) => onMove(e.target.value)}
        >
          {allStages.map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
          <option value="_won">Mark as Won</option>
          <option value="_lost">Mark as Lost</option>
        </select>
      </div>
    </div>
  )
}
