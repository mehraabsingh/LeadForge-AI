import { useQuery } from '@tanstack/react-query'
import { getUsers } from '@/api/auth'
import { useAuth } from '@/hooks/useAuth'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Badge } from '@/components/ui/Badge'
import { Shield, User } from 'lucide-react'

export function SettingsPage() {
  const { user } = useAuth()
  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: getUsers,
    enabled: user?.role === 'ADMIN',
  })

  const ROLE_COLORS: Record<string, 'purple' | 'blue' | 'green'> = {
    ADMIN: 'purple',
    MANAGER: 'blue',
    SALES_REP: 'green',
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      {/* Profile section */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <User className="h-5 w-5 text-indigo-600" />
          <h2 className="font-semibold text-gray-900">My Profile</h2>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase mb-1">Full Name</p>
            <p className="text-gray-900">{user?.full_name}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase mb-1">Email</p>
            <p className="text-gray-900">{user?.email}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 uppercase mb-1">Role</p>
            <Badge variant={ROLE_COLORS[user?.role || 'SALES_REP']}>{user?.role}</Badge>
          </div>
        </div>
      </div>

      {/* User Management (Admin only) */}
      {user?.role === 'ADMIN' && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="h-5 w-5 text-indigo-600" />
            <h2 className="font-semibold text-gray-900">User Management</h2>
          </div>
          {isLoading ? (
            <LoadingSpinner />
          ) : (
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  {['User', 'Email', 'Role', 'Status'].map(h => (
                    <th key={h} className="py-3 pr-6 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users?.users?.map(u => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="py-3 pr-6 font-medium text-gray-900">{u.full_name}</td>
                    <td className="py-3 pr-6 text-gray-600 text-sm">{u.email}</td>
                    <td className="py-3 pr-6">
                      <Badge variant={ROLE_COLORS[u.role]}>{u.role}</Badge>
                    </td>
                    <td className="py-3 pr-6">
                      <Badge variant={u.is_active ? 'green' : 'gray'}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* AI Configuration info */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-6">
        <h2 className="font-semibold text-indigo-900 mb-2">AI Configuration</h2>
        <p className="text-sm text-indigo-700">
          The AI engine is configured via the <code className="bg-indigo-100 px-1 rounded">AI_PROVIDER</code> environment variable on the backend.
          Set to <code className="bg-indigo-100 px-1 rounded">gemini</code> or <code className="bg-indigo-100 px-1 rounded">openai</code> with the corresponding API key.
          The <strong>fallback engine</strong> works without any API key and uses deterministic rule-based scoring.
        </p>
      </div>
    </div>
  )
}
