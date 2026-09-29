import apiClient from './client';
import { Lead, Activity, Note, LeadListResponse, LeadQueryParams } from '../types';

export interface CreateLeadData {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  company?: string;
  job_title?: string;
  source?: string;
  industry?: string;
  company_size?: string;
  location?: string;
  estimated_value?: number;
  status?: string;
  priority?: string;
  description?: string;
  owner_id?: string;
}

export interface CreateActivityData {
  type: string;
  title: string;
  description?: string;
  outcome?: string;
}

export interface CreateNoteData {
  content: string;
}

export async function getLeads(params: LeadQueryParams = {}): Promise<LeadListResponse> {
  const { data } = await apiClient.get<LeadListResponse>('/leads', { params });
  return data;
}

export async function getLead(id: string): Promise<Lead> {
  const { data } = await apiClient.get<Lead>(`/leads/${id}`);
  return data;
}

export async function createLead(payload: CreateLeadData): Promise<Lead> {
  const { data } = await apiClient.post<Lead>('/leads', payload);
  return data;
}

export async function updateLead(id: string, payload: Partial<CreateLeadData>): Promise<Lead> {
  const { data } = await apiClient.put<Lead>(`/leads/${id}`, payload);
  return data;
}

export async function deleteLead(id: string): Promise<void> {
  await apiClient.delete(`/leads/${id}`);
}

export async function getLeadActivities(id: string): Promise<Activity[]> {
  const { data } = await apiClient.get<Activity[]>(`/leads/${id}/activities`);
  return data;
}

export async function createLeadActivity(id: string, payload: CreateActivityData): Promise<Activity> {
  const { data } = await apiClient.post<Activity>(`/leads/${id}/activities`, payload);
  return data;
}

export async function getLeadNotes(id: string): Promise<Note[]> {
  const { data } = await apiClient.get<Note[]>(`/leads/${id}/notes`);
  return data;
}

export async function createLeadNote(id: string, payload: CreateNoteData): Promise<Note> {
  const { data } = await apiClient.post<Note>(`/leads/${id}/notes`, payload);
  return data;
}
