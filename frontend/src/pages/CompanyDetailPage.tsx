import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getCompany, getCompanyContacts, getCompanyActivities } from '@/api/companies'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { ArrowLeft, Building2, Globe, Users, Phone, Mail } from 'lucide-react'
import { formatCurrency, formatDate } from '@/utils/formatters'
import { ACTIVITY_TYPE_LABELS } from '@/utils/constants'

export function CompanyDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: company, isLoading } = useQuery({
    queryKey: ['company', id],
    queryFn: () => getCompany(id!),
    enabled: !!id,
  })

  const { data: contacts } = useQuery({
    queryKey: ['company-contacts', id],
    queryFn: () => getCompanyContacts(id!),
    enabled: !!id,
  })

  const { data: activities } = useQuery({
    queryKey: ['company-activities', id],
    queryFn: () => getCompanyActivities(id!),
    enabled: !!id,
  })

  if (isLoading) return <LoadingSpinner />
  if (!company) return null

  return (
    <div className="space-y-6">
      <Link to="/companies" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="h-4 w-4" /> Back to Companies
      </Link>

      {/* Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-start gap-4">
          <div className="h-16 w-16 rounded-xl bg-indigo-100 flex items-center justify-center">
            <Building2 className="h-8 w-8 text-indigo-600" />
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900">{company.name}</h1>
            <p className="text-gray-500">{company.industry} • {company.size} employees</p>
            {company.description && <p className="mt-2 text-sm text-gray-600">{company.description}</p>}
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          {company.website && (
            <div className="flex items-center gap-2 text-sm">
              <Globe className="h-4 w-4 text-gray-400" />
              <a href={company.website} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline truncate">
                {company.website}
              </a>
            </div>
          )}
          {company.phone && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Phone className="h-4 w-4 text-gray-400" /> {company.phone}
            </div>
          )}
          {company.email && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Mail className="h-4 w-4 text-gray-400" /> {company.email}
            </div>
          )}
          {company.annual_revenue && (
            <div className="text-sm">
              <span className="text-gray-400">Revenue: </span>
              <span className="text-gray-700 font-medium">{formatCurrency(company.annual_revenue)}</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Contacts */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Users className="h-5 w-5 text-indigo-600" /> Contacts ({contacts?.length || 0})
          </h2>
          {contacts?.length ? (
            <div className="space-y-3">
              {contacts.map(c => (
                <div key={c.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="font-medium text-sm text-gray-900">{c.full_name}</p>
                    <p className="text-xs text-gray-500">{c.job_title}</p>
                  </div>
                  <div className="text-right text-xs text-gray-500">
                    {c.email && <p>{c.email}</p>}
                    {c.phone && <p>{c.phone}</p>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No contacts yet</p>
          )}
        </div>

        {/* Recent Activities */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Recent Activities</h2>
          {activities?.length ? (
            <div className="space-y-3">
              {activities.slice(0, 8).map(a => (
                <div key={a.id} className="flex gap-3 py-2 border-b border-gray-100 last:border-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{a.title}</p>
                    <p className="text-xs text-gray-500">
                      {ACTIVITY_TYPE_LABELS[a.type] || a.type} • {formatDate(a.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No activities recorded</p>
          )}
        </div>
      </div>
    </div>
  )
}
