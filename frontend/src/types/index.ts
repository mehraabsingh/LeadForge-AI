// ─── Enums / Union Types ────────────────────────────────────────────────────

export type UserRole = 'ADMIN' | 'MANAGER' | 'SALES_REP';

export type LeadStatus =
  | 'NEW'
  | 'CONTACTED'
  | 'QUALIFIED'
  | 'UNQUALIFIED'
  | 'CONVERTED'
  | 'LOST';

export type LeadPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export type LeadSource =
  | 'WEBSITE'
  | 'REFERRAL'
  | 'LINKEDIN'
  | 'COLD_OUTREACH'
  | 'CONFERENCE'
  | 'ADVERTISEMENT'
  | 'PARTNER'
  | 'OTHER';

export type OpportunityStatus = 'OPEN' | 'WON' | 'LOST';

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';

export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export type ActivityType =
  | 'CALL'
  | 'EMAIL'
  | 'MEETING'
  | 'NOTE'
  | 'FOLLOW_UP'
  | 'DEMO'
  | 'PROPOSAL'
  | 'OTHER';

// ─── Core Entities ───────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Lead {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone?: string;
  company?: string;
  job_title?: string;
  source?: LeadSource;
  industry?: string;
  company_size?: string;
  location?: string;
  estimated_value?: number;
  status: LeadStatus;
  priority: LeadPriority;
  score?: number;
  score_label?: string;
  description?: string;
  owner_id?: string;
  owner?: { id: string; full_name: string; email: string };
  company_id?: string;
  activity_count?: number;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  name: string;
  industry?: string;
  website?: string;
  size?: string;
  location?: string;
  annual_revenue?: number;
  description?: string;
  phone?: string;
  email?: string;
  linkedin_url?: string;
  contact_count?: number;
  lead_count?: number;
  created_at: string;
  updated_at: string;
}

export interface Contact {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email?: string;
  phone?: string;
  job_title?: string;
  company_id?: string;
  company_name?: string;
  linkedin_url?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface PipelineStage {
  id: string;
  name: string;
  order: number;
  color?: string;
  probability: number;
  pipeline_id: string;
  opportunity_count: number;
  stage_value: number;
}

export interface Pipeline {
  id: string;
  name: string;
  description?: string;
  is_default: boolean;
  stages: PipelineStage[];
  created_at: string;
  updated_at: string;
}

export interface Opportunity {
  id: string;
  title: string;
  description?: string;
  value?: number;
  probability?: number;
  status: OpportunityStatus;
  expected_close_date?: string;
  actual_close_date?: string;
  notes?: string;
  lead_id?: string;
  pipeline_id?: string;
  stage_id?: string;
  stage?: { id: string; name: string; color?: string; probability: number };
  company_id?: string;
  owner_id?: string;
  owner?: { id: string; full_name: string; email: string };
  weighted_value?: number;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_date?: string;
  lead_id?: string;
  lead_name?: string;
  opportunity_id?: string;
  assigned_to_id?: string;
  assigned_to?: { id: string; full_name: string; email: string };
  created_by_id?: string;
  is_overdue?: boolean;
  created_at: string;
  updated_at: string;
}

export interface Activity {
  id: string;
  type: ActivityType;
  title: string;
  description?: string;
  outcome?: string;
  lead_id?: string;
  company_id?: string;
  opportunity_id?: string;
  user_id?: string;
  user?: { id: string; full_name: string };
  created_at: string;
}

export interface Note {
  id: string;
  content: string;
  lead_id?: string;
  company_id?: string;
  opportunity_id?: string;
  author_id?: string;
  author_name?: string;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  link?: string;
  user_id: string;
  created_at: string;
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface DashboardStats {
  total_leads: number;
  new_leads: number;
  qualified_leads: number;
  converted_leads: number;
  open_opportunities: number;
  pipeline_value: number;
  weighted_pipeline: number;
  won_revenue: number;
  win_rate: number;
  conversion_rate: number;
  avg_deal_size: number;
  open_tasks: number;
  overdue_tasks: number;
  leads_this_month: number;
}

export interface DashboardCharts {
  leads_over_time: Array<{ month: string; leads: number }>;
  revenue_by_month: Array<{ month: string; revenue: number }>;
  pipeline_by_stage: Array<{ stage: string; value: number; count: number; color: string }>;
  lead_sources: Array<{ source: string; count: number }>;
  opportunity_status: Array<{ status: string; count: number; value: number }>;
  rep_performance: Array<{ name: string; leads: number; won_deals: number; revenue: number }>;
}

// ─── AI Types ─────────────────────────────────────────────────────────────────

export interface LeadScore {
  lead_id: string;
  score: number;
  label: string;
  explanation: string;
  key_factors: string[];
  recommended_action: string;
  provider: string;
}

export interface LeadSummary {
  lead_id: string;
  profile_summary: string;
  activity_summary: string;
  pipeline_status: string;
  key_risks: string[];
  recommended_next_step: string;
  overall_assessment: string;
  provider: string;
}

export interface FollowUpEmail {
  lead_id: string;
  email_type: string;
  subject: string;
  body: string;
  provider: string;
}

export interface SalesInsight {
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  action: string;
  lead_ids?: string[];
  opp_ids?: string[];
}

export interface SalesInsightsResponse {
  total_insights: number;
  insights: SalesInsight[];
  generated_at?: string;
  provider: string;
}

// ─── API Responses ────────────────────────────────────────────────────────────

export interface LeadListResponse {
  leads: Lead[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface OpportunityListResponse {
  opportunities: Opportunity[];
  total: number;
  pipeline_value: number;
  weighted_value: number;
  won_value: number;
  win_rate: number;
}

// ─── Query Params ─────────────────────────────────────────────────────────────

export interface LeadQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  priority?: string;
  source?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface GenericQueryParams {
  search?: string;
  [key: string]: string | number | undefined;
}

// ─── API Error ────────────────────────────────────────────────────────────────

export interface ApiError {
  message: string;
  status: number;
  detail?: string | Record<string, unknown>;
}
