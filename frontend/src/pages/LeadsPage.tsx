import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Search } from 'lucide-react';
import { getLeads, createLead } from '@/api/leads';
import type { Lead, LeadQueryParams } from '@/types';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ScoreBadge } from '@/components/ui/ScoreBadge';
import { Pagination } from '@/components/ui/Pagination';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { Modal } from '@/components/ui/Modal';
import { LeadForm } from '@/features/leads/LeadForm';
import { LEAD_STATUS_LABELS, LEAD_PRIORITY_LABELS, LEAD_SOURCE_LABELS } from '@/utils/constants';
import { formatDate, formatCurrency } from '@/utils/formatters';
import clsx from 'clsx';

export function LeadsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [source, setSource] = useState('');
  const [page, setPage] = useState(1);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Debounce search
  let searchTimer: ReturnType<typeof setTimeout>;
  const handleSearch = useCallback((val: string) => {
    setSearch(val);
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      setDebouncedSearch(val);
      setPage(1);
    }, 400);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const params: LeadQueryParams = {
    page,
    page_size: 20,
    search: debouncedSearch || undefined,
    status: status || undefined,
    priority: priority || undefined,
    source: source || undefined,
  };

  const { data, isLoading } = useQuery({
    queryKey: ['leads', params],
    queryFn: () => getLeads(params),
  });

  const createMutation = useMutation({
    mutationFn: createLead,
    onSuccess: () => {
      setIsCreateOpen(false);
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });

  const leads = data?.leads ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
        <Button variant="primary" onClick={() => setIsCreateOpen(true)}>
          <Plus className="h-4 w-4" /> New Lead
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search leads..."
            value={search}
            onChange={(e) => handleSearch(e.target.value)}
            className="input-field pl-10"
          />
        </div>
        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          className="input-field w-40"
        >
          <option value="">All Statuses</option>
          {Object.entries(LEAD_STATUS_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
        <select
          value={priority}
          onChange={(e) => { setPriority(e.target.value); setPage(1); }}
          className="input-field w-36"
        >
          <option value="">All Priorities</option>
          {Object.entries(LEAD_PRIORITY_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
        <select
          value={source}
          onChange={(e) => { setSource(e.target.value); setPage(1); }}
          className="input-field w-40"
        >
          <option value="">All Sources</option>
          {Object.entries(LEAD_SOURCE_LABELS).map(([v, l]) => (
            <option key={v} value={v}>{l}</option>
          ))}
        </select>
        {data && (
          <span className="text-sm text-gray-500 ml-auto">{data.total} leads</span>
        )}
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <LoadingSpinner />
        ) : leads.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="font-medium">No leads found</p>
            <p className="text-sm mt-1">Try adjusting your filters or create a new lead</p>
          </div>
        ) : (
          <>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['Name', 'Company', 'Status', 'Priority', 'Score', 'Value', 'Owner', 'Created'].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {leads.map((lead: Lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => navigate(`/leads/${lead.id}`)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-gray-900">{lead.full_name}</p>
                        {lead.job_title && <p className="text-xs text-gray-500">{lead.job_title}</p>}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{lead.company || '—'}</td>
                    <td className="px-4 py-3">
                      <Badge status={lead.status} label={LEAD_STATUS_LABELS[lead.status] || lead.status} />
                    </td>
                    <td className="px-4 py-3">
                      <Badge status={lead.priority} label={LEAD_PRIORITY_LABELS[lead.priority] || lead.priority} />
                    </td>
                    <td className="px-4 py-3">
                      {lead.score != null ? (
                        <ScoreBadge score={lead.score} label={lead.score_label || ''} />
                      ) : (
                        <span className="text-xs text-gray-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {lead.estimated_value ? formatCurrency(lead.estimated_value) : '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {lead.owner?.full_name || '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-400">
                      {formatDate(lead.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {data && data.total_pages > 1 && (
              <div className="px-4 py-3 border-t border-gray-200">
                <Pagination
                  page={data.page}
                  totalPages={data.total_pages}
                  total={data.total}
                  pageSize={data.page_size}
                  onPageChange={setPage}
                />
              </div>
            )}
          </>
        )}
      </div>

      {/* Create Lead Modal */}
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="New Lead">
        <LeadForm
          onSubmit={(formData) => createMutation.mutate(formData)}
          isLoading={createMutation.isPending}
          submitLabel="Create Lead"
        />
      </Modal>
    </div>
  );
}
