import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Brain, Mail, MessageSquare, Plus, Star, Edit, Trash2, Copy, Check } from 'lucide-react';
import { getLead, getLeadActivities, getLeadNotes, createLeadActivity, createLeadNote } from '@/api/leads';
import { scoreLead, summarizeLead, generateFollowUpEmail } from '@/api/ai';
import { getTasks } from '@/api/tasks';
import { Badge } from '@/components/ui/Badge';
import { ScoreBadge } from '@/components/ui/ScoreBadge';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ActivityForm } from '@/features/leads/ActivityForm';
import { NoteForm } from '@/features/leads/NoteForm';
import { LeadForm } from '@/features/leads/LeadForm';
import { updateLead } from '@/api/leads';
import { LEAD_STATUS_LABELS, LEAD_PRIORITY_LABELS, ACTIVITY_TYPE_LABELS } from '@/utils/constants';
import { formatCurrency, formatRelativeDate, formatDate } from '@/utils/formatters';
import clsx from 'clsx';

type AIView = 'score' | 'summary' | 'email' | null;
type EmailType = 'introduction' | 'follow_up' | 'proposal' | 're_engagement';

export function LeadDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isActivityOpen, setIsActivityOpen] = useState(false);
  const [isNoteOpen, setIsNoteOpen] = useState(false);
  const [aiView, setAiView] = useState<AIView>(null);
  const [emailType, setEmailType] = useState<EmailType>('follow_up');
  const [copiedEmail, setCopiedEmail] = useState(false);

  const { data: lead, isLoading } = useQuery({
    queryKey: ['lead', id],
    queryFn: () => getLead(id!),
    enabled: !!id,
  });

  const { data: activities } = useQuery({
    queryKey: ['lead-activities', id],
    queryFn: () => getLeadActivities(id!),
    enabled: !!id,
  });

  const { data: notes } = useQuery({
    queryKey: ['lead-notes', id],
    queryFn: () => getLeadNotes(id!),
    enabled: !!id,
  });

  const { data: tasks } = useQuery({
    queryKey: ['tasks', { lead_id: id }],
    queryFn: () => getTasks({ lead_id: id }),
    enabled: !!id,
  });

  const scoreQuery = useQuery({
    queryKey: ['ai-score', id],
    queryFn: () => scoreLead(id!),
    enabled: aiView === 'score' && !!id,
  });

  const summaryQuery = useQuery({
    queryKey: ['ai-summary', id],
    queryFn: () => summarizeLead(id!),
    enabled: aiView === 'summary' && !!id,
  });

  const emailQuery = useQuery({
    queryKey: ['ai-email', id, emailType],
    queryFn: () => generateFollowUpEmail(id!, emailType),
    enabled: aiView === 'email' && !!id,
  });

  const logActivity = useMutation({
    mutationFn: (data: Parameters<typeof createLeadActivity>[1]) => createLeadActivity(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead-activities', id] });
      setIsActivityOpen(false);
    },
  });

  const addNote = useMutation({
    mutationFn: (data: Parameters<typeof createLeadNote>[1]) => createLeadNote(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead-notes', id] });
      setIsNoteOpen(false);
    },
  });

  const editLead = useMutation({
    mutationFn: (data: Parameters<typeof updateLead>[1]) => updateLead(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lead', id] });
      setIsEditOpen(false);
    },
  });

  const copyEmail = (body: string) => {
    navigator.clipboard.writeText(body);
    setCopiedEmail(true);
    setTimeout(() => setCopiedEmail(false), 2000);
  };

  if (isLoading) return <LoadingSpinner />;
  if (!lead) return <div className="text-center py-16 text-gray-500">Lead not found</div>;

  // Timeline: merge activities and notes, sort by date
  type TimelineItem =
    | { kind: 'activity'; id: string; title: string; description?: string; type: string; outcome?: string; user?: { full_name: string }; created_at: string }
    | { kind: 'note'; id: string; content: string; author_name?: string; created_at: string };

  const timeline: TimelineItem[] = [
    ...(activities?.map(a => ({ ...a, kind: 'activity' as const })) ?? []),
    ...(notes?.map(n => ({ ...n, kind: 'note' as const })) ?? []),
  ].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <Link to="/leads" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="h-4 w-4" /> Back to Leads
      </Link>

      {/* Header card */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold text-gray-900">{lead.full_name}</h1>
              <Badge status={lead.status} label={LEAD_STATUS_LABELS[lead.status] || lead.status} />
              <Badge status={lead.priority} label={LEAD_PRIORITY_LABELS[lead.priority] || lead.priority} />
              {lead.score != null && (
                <ScoreBadge score={lead.score} label={lead.score_label || ''} />
              )}
            </div>
            {lead.job_title && <p className="text-gray-500 mt-1">{lead.job_title}</p>}
            {lead.company && (
              <p className="text-indigo-600 font-medium mt-0.5">{lead.company}</p>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setIsEditOpen(true)}>
              <Edit className="h-4 w-4" /> Edit
            </Button>
          </div>
        </div>

        {/* Info grid */}
        <div className="mt-5 grid grid-cols-2 md:grid-cols-4 gap-4 pt-5 border-t border-gray-100">
          {lead.email && (
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-0.5">Email</p>
              <a href={`mailto:${lead.email}`} className="text-sm text-indigo-600 hover:underline">{lead.email}</a>
            </div>
          )}
          {lead.phone && (
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-0.5">Phone</p>
              <a href={`tel:${lead.phone}`} className="text-sm text-gray-700">{lead.phone}</a>
            </div>
          )}
          {lead.estimated_value && (
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-0.5">Deal Value</p>
              <p className="text-sm font-semibold text-green-600">{formatCurrency(lead.estimated_value)}</p>
            </div>
          )}
          {lead.source && (
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-0.5">Source</p>
              <p className="text-sm text-gray-700">{lead.source}</p>
            </div>
          )}
          {lead.location && (
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-0.5">Location</p>
              <p className="text-sm text-gray-700">{lead.location}</p>
            </div>
          )}
          {lead.industry && (
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-0.5">Industry</p>
              <p className="text-sm text-gray-700">{lead.industry}</p>
            </div>
          )}
          {lead.owner && (
            <div>
              <p className="text-xs text-gray-400 font-medium uppercase mb-0.5">Owner</p>
              <p className="text-sm text-gray-700">{lead.owner.full_name}</p>
            </div>
          )}
          <div>
            <p className="text-xs text-gray-400 font-medium uppercase mb-0.5">Created</p>
            <p className="text-sm text-gray-700">{formatDate(lead.created_at)}</p>
          </div>
        </div>

        {lead.description && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <p className="text-sm text-gray-600">{lead.description}</p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline */}
        <div className="lg:col-span-2 space-y-4">
          {/* Actions row */}
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => setIsActivityOpen(true)}>
              <Plus className="h-4 w-4" /> Log Activity
            </Button>
            <Button variant="secondary" onClick={() => setIsNoteOpen(true)}>
              <MessageSquare className="h-4 w-4" /> Add Note
            </Button>
          </div>

          {/* Timeline items */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="font-semibold text-gray-900 mb-4">Activity Timeline</h2>
            {timeline.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-8">No activities or notes yet</p>
            ) : (
              <div className="space-y-4">
                {timeline.map((item) => (
                  <div key={`${item.kind}-${item.id}`} className="flex gap-3">
                    <div className={clsx(
                      'mt-1 h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold',
                      item.kind === 'activity' ? 'bg-indigo-100 text-indigo-700' : 'bg-green-100 text-green-700'
                    )}>
                      {item.kind === 'activity' ? '⚡' : '📝'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm text-gray-900">
                          {item.kind === 'activity'
                            ? `${ACTIVITY_TYPE_LABELS[item.type as keyof typeof ACTIVITY_TYPE_LABELS] || item.type}: ${item.title}`
                            : 'Note'}
                        </span>
                        <span className="text-xs text-gray-400">{formatRelativeDate(item.created_at)}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-0.5">
                        {item.kind === 'activity' ? item.description : item.content}
                      </p>
                      {item.kind === 'activity' && item.outcome && (
                        <p className="text-xs text-gray-400 mt-1 italic">→ {item.outcome}</p>
                      )}
                      {item.kind === 'activity' && item.user && (
                        <p className="text-xs text-gray-400 mt-1">by {item.user.full_name}</p>
                      )}
                      {item.kind === 'note' && item.author_name && (
                        <p className="text-xs text-gray-400 mt-1">by {item.author_name}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Tasks */}
          {tasks && tasks.length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="font-semibold text-gray-900 mb-4">Related Tasks ({tasks.length})</h2>
              <div className="space-y-2">
                {tasks.map((task) => (
                  <div key={task.id} className={clsx(
                    'flex items-center gap-3 py-2 border-b border-gray-100 last:border-0',
                    task.is_overdue && 'text-red-600'
                  )}>
                    <div className={clsx(
                      'h-4 w-4 rounded border-2',
                      task.status === 'COMPLETED' ? 'bg-green-500 border-green-500' : 'border-gray-300'
                    )} />
                    <span className="flex-1 text-sm">{task.title}</span>
                    <Badge status={task.priority} label={task.priority} size="sm" />
                    {task.due_date && (
                      <span className="text-xs text-gray-400">{formatDate(task.due_date)}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* AI Panel */}
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="h-5 w-5 text-indigo-600" />
              <h2 className="font-semibold text-gray-900">AI Analysis</h2>
            </div>

            <div className="space-y-2">
              <Button
                variant={aiView === 'score' ? 'primary' : 'secondary'}
                className="w-full justify-start"
                onClick={() => setAiView(aiView === 'score' ? null : 'score')}
              >
                <Star className="h-4 w-4" /> Score Lead
              </Button>
              <Button
                variant={aiView === 'summary' ? 'primary' : 'secondary'}
                className="w-full justify-start"
                onClick={() => setAiView(aiView === 'summary' ? null : 'summary')}
              >
                <Brain className="h-4 w-4" /> AI Summary
              </Button>
              <Button
                variant={aiView === 'email' ? 'primary' : 'secondary'}
                className="w-full justify-start"
                onClick={() => setAiView(aiView === 'email' ? null : 'email')}
              >
                <Mail className="h-4 w-4" /> Generate Email
              </Button>
            </div>

            {/* AI Score */}
            {aiView === 'score' && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                {scoreQuery.isLoading ? (
                  <LoadingSpinner />
                ) : scoreQuery.data ? (
                  <div className="space-y-3">
                    <div className="text-center">
                      <span className="text-4xl font-bold text-indigo-600">{scoreQuery.data.score}</span>
                      <span className="text-gray-400">/100</span>
                      <p className={clsx(
                        'font-bold text-lg mt-1',
                        scoreQuery.data.label === 'HOT' ? 'text-red-500' :
                        scoreQuery.data.label === 'WARM' ? 'text-orange-500' : 'text-blue-500'
                      )}>
                        {scoreQuery.data.label}
                      </p>
                    </div>
                    <p className="text-sm text-gray-600">{scoreQuery.data.explanation}</p>
                    {scoreQuery.data.key_factors.length > 0 && (
                      <ul className="text-xs text-gray-500 list-disc pl-4 space-y-1">
                        {scoreQuery.data.key_factors.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    )}
                    <div className="bg-indigo-50 rounded-lg p-3">
                      <p className="text-xs font-semibold text-indigo-700">Recommended Action</p>
                      <p className="text-xs text-indigo-600 mt-1">{scoreQuery.data.recommended_action}</p>
                    </div>
                  </div>
                ) : null}
              </div>
            )}

            {/* AI Summary */}
            {aiView === 'summary' && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                {summaryQuery.isLoading ? (
                  <LoadingSpinner />
                ) : summaryQuery.data ? (
                  <div className="space-y-3 text-sm">
                    <p className="text-gray-700">{summaryQuery.data.profile_summary}</p>
                    {summaryQuery.data.key_risks.length > 0 && (
                      <div>
                        <p className="font-medium text-orange-600 text-xs uppercase mb-1">Key Risks</p>
                        <ul className="text-xs text-gray-600 list-disc pl-4 space-y-1">
                          {summaryQuery.data.key_risks.map((r, i) => (
                            <li key={i}>{r}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div className="bg-green-50 rounded-lg p-3">
                      <p className="text-xs font-semibold text-green-700">Next Step</p>
                      <p className="text-xs text-green-600 mt-1">{summaryQuery.data.recommended_next_step}</p>
                    </div>
                  </div>
                ) : null}
              </div>
            )}

            {/* AI Email */}
            {aiView === 'email' && (
              <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                <select
                  value={emailType}
                  onChange={(e) => setEmailType(e.target.value as EmailType)}
                  className="input-field text-sm"
                >
                  <option value="introduction">Introduction</option>
                  <option value="follow_up">Follow Up</option>
                  <option value="proposal">Proposal</option>
                  <option value="re_engagement">Re-Engagement</option>
                </select>
                {emailQuery.isLoading ? (
                  <LoadingSpinner />
                ) : emailQuery.data ? (
                  <div className="space-y-2">
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Subject</p>
                      <p className="text-sm font-medium text-gray-800">{emailQuery.data.subject}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs font-semibold text-gray-500 uppercase mb-1">Body</p>
                      <p className="text-xs text-gray-700 whitespace-pre-line leading-relaxed">{emailQuery.data.body}</p>
                    </div>
                    <Button
                      variant="secondary"
                      className="w-full"
                      onClick={() => copyEmail(emailQuery.data!.body)}
                    >
                      {copiedEmail ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                      {copiedEmail ? 'Copied!' : 'Copy Email'}
                    </Button>
                  </div>
                ) : null}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} title="Edit Lead">
        <LeadForm
          onSubmit={(data) => editLead.mutate(data)}
          isLoading={editLead.isPending}
          defaultValues={{
            first_name: lead.first_name,
            last_name: lead.last_name,
            email: lead.email,
            phone: lead.phone,
            company: lead.company,
            job_title: lead.job_title,
            source: lead.source,
            industry: lead.industry,
            company_size: lead.company_size,
            estimated_value: lead.estimated_value,
            status: lead.status,
            priority: lead.priority,
            description: lead.description,
          }}
          submitLabel="Save Changes"
        />
      </Modal>

      <Modal isOpen={isActivityOpen} onClose={() => setIsActivityOpen(false)} title="Log Activity">
        <ActivityForm
          onSubmit={(data) => logActivity.mutate(data)}
          isLoading={logActivity.isPending}
          onCancel={() => setIsActivityOpen(false)}
        />
      </Modal>

      <Modal isOpen={isNoteOpen} onClose={() => setIsNoteOpen(false)} title="Add Note">
        <NoteForm
          onSubmit={(data) => addNote.mutate(data)}
          isLoading={addNote.isPending}
          onCancel={() => setIsNoteOpen(false)}
        />
      </Modal>
    </div>
  );
}
