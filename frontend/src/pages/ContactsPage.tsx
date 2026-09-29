import { useQuery } from '@tanstack/react-query'
import { getContacts } from '@/api/contacts'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { Users } from 'lucide-react'
import { useState } from 'react'

export function ContactsPage() {
  const [search, setSearch] = useState('')

  const { data: contacts, isLoading } = useQuery({
    queryKey: ['contacts', search],
    queryFn: () => getContacts({ search }),
  })

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Contacts</h1>
        <span className="text-sm text-gray-500">{contacts?.length || 0} contacts</span>
      </div>

      <input
        type="text"
        placeholder="Search contacts..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="input-field max-w-xs"
      />

      {!contacts?.length ? (
        <EmptyState
          icon={<Users className="h-12 w-12 text-gray-400" />}
          title="No contacts found"
          description="Contacts will appear here when you add them to companies"
        />
      ) : (
        <div className="bg-white shadow-sm rounded-xl overflow-hidden border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Name', 'Job Title', 'Email', 'Phone', 'Company'].map(h => (
                  <th key={h} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {contacts.map((contact) => (
                <tr key={contact.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <span className="font-medium text-gray-900">{contact.full_name}</span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{contact.job_title || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{contact.email || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{contact.phone || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{contact.company_name || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
