import { useQuery } from '@tanstack/react-query'
import { getCompanies } from '@/api/companies'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { Building2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { formatCurrency } from '@/utils/formatters'

export function CompaniesPage() {
  const [search, setSearch] = useState('')

  const { data: companies, isLoading } = useQuery({
    queryKey: ['companies', search],
    queryFn: () => getCompanies({ search }),
  })

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Companies</h1>
        <span className="text-sm text-gray-500">{companies?.length || 0} companies</span>
      </div>

      <input
        type="text"
        placeholder="Search companies..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="input-field max-w-xs"
      />

      {!companies?.length ? (
        <EmptyState
          icon={<Building2 className="h-12 w-12 text-gray-400" />}
          title="No companies found"
          description="Add your first company to get started"
        />
      ) : (
        <div className="bg-white shadow-sm rounded-xl overflow-hidden border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Company', 'Industry', 'Size', 'Location', 'Revenue', 'Contacts', 'Leads'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {companies.map((company) => (
                <tr key={company.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <Link to={`/companies/${company.id}`} className="font-medium text-indigo-600 hover:text-indigo-800">
                      {company.name}
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{company.industry || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{company.size || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{company.location || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {company.annual_revenue ? formatCurrency(company.annual_revenue) : '—'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{company.contact_count ?? 0}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{company.lead_count ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
