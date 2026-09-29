import apiClient from './client';
import { LeadScore, LeadSummary, FollowUpEmail, SalesInsightsResponse } from '../types';

export async function scoreLead(leadId: string): Promise<LeadScore> {
  const { data } = await apiClient.post<LeadScore>(`/ai/leads/${leadId}/score`);
  return data;
}

export async function summarizeLead(leadId: string): Promise<LeadSummary> {
  const { data } = await apiClient.post<LeadSummary>(`/ai/leads/${leadId}/summary`);
  return data;
}

export async function generateFollowUpEmail(leadId: string, emailType: string): Promise<FollowUpEmail> {
  const { data } = await apiClient.post<FollowUpEmail>(`/ai/leads/${leadId}/follow-up-email`, { email_type: emailType });
  return data;
}

export async function getSalesInsights(): Promise<SalesInsightsResponse> {
  const { data } = await apiClient.get<SalesInsightsResponse>('/ai/insights');
  return data;
}
