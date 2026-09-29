import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTasks, updateTask } from '@/api/tasks'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { Badge } from '@/components/ui/Badge'
import { CheckSquare, Clock, AlertCircle } from 'lucide-react'
import { formatDate } from '@/utils/formatters'
import { useState } from 'react'
import { TaskStatus } from '@/types'
import clsx from 'clsx'

export function TasksPage() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<string>('')

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', statusFilter],
    queryFn: () => getTasks({ status: statusFilter || undefined }),
  })

  const toggleComplete = useMutation({
    mutationFn: ({ id, status }: { id: string; status: TaskStatus }) =>
      updateTask(id, { status }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  })

  if (isLoading) return <LoadingSpinner />

  const overdue = tasks?.filter(t => t.is_overdue) ?? []
  const pending = tasks?.filter(t => !t.is_overdue && t.status !== 'COMPLETED') ?? []
  const completed = tasks?.filter(t => t.status === 'COMPLETED') ?? []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
        <div className="flex gap-2">
          {['', 'TODO', 'IN_PROGRESS', 'COMPLETED'].map(s => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={clsx('px-3 py-1.5 text-sm rounded-lg border transition-colors',
                statusFilter === s
                  ? 'bg-indigo-600 text-white border-indigo-600'
                  : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
              )}
            >
              {s || 'All'}
            </button>
          ))}
        </div>
      </div>

      {!tasks?.length ? (
        <EmptyState
          icon={<CheckSquare className="h-12 w-12 text-gray-400" />}
          title="No tasks found"
          description="Create tasks to track your follow-ups"
        />
      ) : (
        <div className="space-y-4">
          {overdue.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-red-600 mb-2 flex items-center gap-1.5">
                <AlertCircle className="h-4 w-4" /> Overdue ({overdue.length})
              </h2>
              <div className="space-y-2">
                {overdue.map(task => (
                  <TaskCard key={task.id} task={task} onToggle={toggleComplete.mutate} />
                ))}
              </div>
            </div>
          )}

          {pending.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-1.5">
                <Clock className="h-4 w-4" /> Pending ({pending.length})
              </h2>
              <div className="space-y-2">
                {pending.map(task => (
                  <TaskCard key={task.id} task={task} onToggle={toggleComplete.mutate} />
                ))}
              </div>
            </div>
          )}

          {completed.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-gray-400 mb-2 flex items-center gap-1.5">
                <CheckSquare className="h-4 w-4" /> Completed ({completed.length})
              </h2>
              <div className="space-y-2 opacity-60">
                {completed.map(task => (
                  <TaskCard key={task.id} task={task} onToggle={toggleComplete.mutate} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function TaskCard({
  task,
  onToggle,
}: {
  task: any
  onToggle: (args: { id: string; status: TaskStatus }) => void
}) {
  const isDone = task.status === 'COMPLETED'
  const isOverdue = task.is_overdue

  return (
    <div className={clsx(
      'bg-white rounded-xl border p-4 flex items-start gap-4 hover:shadow-sm transition-shadow',
      isOverdue ? 'border-red-200' : 'border-gray-200'
    )}>
      <button
        onClick={() => onToggle({
          id: task.id,
          status: isDone ? 'TODO' : 'COMPLETED',
        })}
        className={clsx(
          'mt-0.5 h-5 w-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors',
          isDone ? 'bg-green-500 border-green-500' : 'border-gray-300 hover:border-indigo-500'
        )}
      >
        {isDone && <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
        </svg>}
      </button>

      <div className="flex-1 min-w-0">
        <p className={clsx('font-medium text-gray-900', isDone && 'line-through text-gray-400')}>
          {task.title}
        </p>
        {task.description && (
          <p className="text-sm text-gray-500 mt-0.5 truncate">{task.description}</p>
        )}
        <div className="flex items-center gap-3 mt-2">
          <Badge
            variant={task.priority === 'URGENT' ? 'red' : task.priority === 'HIGH' ? 'orange' : task.priority === 'MEDIUM' ? 'blue' : 'gray'}
          >
            {task.priority}
          </Badge>
          {task.due_date && (
            <span className={clsx('text-xs', isOverdue ? 'text-red-600 font-medium' : 'text-gray-400')}>
              {isOverdue ? '⚠️ Due: ' : 'Due: '}{formatDate(task.due_date)}
            </span>
          )}
          {task.assigned_to && (
            <span className="text-xs text-gray-400">→ {task.assigned_to.full_name}</span>
          )}
          {task.lead_name && (
            <span className="text-xs text-indigo-500">Lead: {task.lead_name}</span>
          )}
        </div>
      </div>
    </div>
  )
}
