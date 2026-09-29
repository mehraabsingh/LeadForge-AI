import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

const schema = z.object({
  first_name: z.string().min(1, 'First name required'),
  last_name: z.string().min(1, 'Last name required'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  phone: z.string().optional(),
  company: z.string().optional(),
  job_title: z.string().optional(),
  source: z.string().optional(),
  industry: z.string().optional(),
  company_size: z.string().optional(),
  estimated_value: z.coerce.number().optional(),
  status: z.string().default('NEW'),
  priority: z.string().default('MEDIUM'),
  description: z.string().optional(),
})

type FormData = z.infer<typeof schema>

interface LeadFormProps {
  onSubmit: (data: FormData) => void
  isLoading?: boolean
  defaultValues?: Partial<FormData>
  submitLabel?: string
}

export function LeadForm({ onSubmit, isLoading, defaultValues, submitLabel = 'Save Lead' }: LeadFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: defaultValues || { status: 'NEW', priority: 'MEDIUM' },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input label="First Name" error={errors.first_name?.message} {...register('first_name')} />
        <Input label="Last Name" error={errors.last_name?.message} {...register('last_name')} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input label="Email" type="email" error={errors.email?.message} {...register('email')} />
        <Input label="Phone" {...register('phone')} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input label="Company" {...register('company')} />
        <Input label="Job Title" {...register('job_title')} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Status</label>
          <select {...register('status')} className="input-field">
            <option value="NEW">New</option>
            <option value="CONTACTED">Contacted</option>
            <option value="QUALIFIED">Qualified</option>
            <option value="UNQUALIFIED">Unqualified</option>
            <option value="CONVERTED">Converted</option>
            <option value="LOST">Lost</option>
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Priority</label>
          <select {...register('priority')} className="input-field">
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="URGENT">Urgent</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Source</label>
          <select {...register('source')} className="input-field">
            <option value="">— Select source —</option>
            <option value="WEBSITE">Website</option>
            <option value="REFERRAL">Referral</option>
            <option value="LINKEDIN">LinkedIn</option>
            <option value="COLD_OUTREACH">Cold Outreach</option>
            <option value="CONFERENCE">Conference</option>
            <option value="PARTNER">Partner</option>
            <option value="OTHER">Other</option>
          </select>
        </div>
        <Input label="Estimated Value ($)" type="number" {...register('estimated_value')} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <Input label="Industry" {...register('industry')} />
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Company Size</label>
          <select {...register('company_size')} className="input-field">
            <option value="">— Select size —</option>
            <option value="1-10">1-10</option>
            <option value="11-50">11-50</option>
            <option value="51-200">51-200</option>
            <option value="201-500">201-500</option>
            <option value="500+">500+</option>
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          {...register('description')}
          className="input-field min-h-[80px] resize-y"
          placeholder="Notes about this lead..."
        />
      </div>
      <div className="flex justify-end">
        <Button type="submit" variant="primary" disabled={isLoading} isLoading={isLoading}>
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}
