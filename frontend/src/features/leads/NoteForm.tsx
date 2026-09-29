import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/Button'

const schema = z.object({
  content: z.string().min(1, 'Note content required'),
})

type FormData = z.infer<typeof schema>

interface NoteFormProps {
  onSubmit: (data: FormData) => void
  isLoading?: boolean
  onCancel?: () => void
}

export function NoteForm({ onSubmit, isLoading, onCancel }: NoteFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Note</label>
        <textarea
          {...register('content')}
          className="input-field min-h-[120px] resize-y"
          placeholder="Add a note about this lead..."
          autoFocus
        />
        {errors.content && <p className="text-xs text-red-500 mt-1">{errors.content.message}</p>}
      </div>
      <div className="flex gap-3 justify-end">
        {onCancel && <Button type="button" variant="secondary" onClick={onCancel}>Cancel</Button>}
        <Button type="submit" variant="primary" disabled={isLoading} isLoading={isLoading}>Add Note</Button>
      </div>
    </form>
  )
}
