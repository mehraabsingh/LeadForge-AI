import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

const schema = z.object({
  type: z.string().min(1),
  title: z.string().min(1, 'Title required'),
  description: z.string().optional(),
  outcome: z.string().optional(),
})

type FormData = z.infer<typeof schema>

interface ActivityFormProps {
  onSubmit: (data: FormData) => void
  isLoading?: boolean
  onCancel?: () => void
}

export function ActivityForm({ onSubmit, isLoading, onCancel }: ActivityFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { type: 'CALL' },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Activity Type</label>
          <select {...register('type')} className="input-field">
            <option value="CALL">📞 Call</option>
            <option value="EMAIL">📧 Email</option>
            <option value="MEETING">🤝 Meeting</option>
            <option value="DEMO">💻 Demo</option>
            <option value="FOLLOW_UP">📋 Follow Up</option>
            <option value="PROPOSAL">📄 Proposal</option>
            <option value="NOTE">📝 Note</option>
            <option value="OTHER">Other</option>
          </select>
        </div>
        <Input label="Title" error={errors.title?.message} {...register('title')} placeholder="e.g. Initial discovery call" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea {...register('description')} className="input-field min-h-[80px] resize-y" placeholder="What happened?" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Outcome</label>
        <textarea {...register('outcome')} className="input-field min-h-[60px] resize-y" placeholder="What was the result?" />
      </div>
      <div className="flex gap-3 justify-end">
        {onCancel && <Button type="button" variant="secondary" onClick={onCancel}>Cancel</Button>}
        <Button type="submit" variant="primary" disabled={isLoading} isLoading={isLoading}>Log Activity</Button>
      </div>
    </form>
  )
}
