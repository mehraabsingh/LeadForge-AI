import apiClient from './client';
import { Opportunity, OpportunityListResponse, GenericQueryParams } from '../types';

export interface CreateOpportunityData {
  title: string;
  value?: number;
  status?: string;
  probability?: number;
  expected_close_date?: string;
  pipeline_id?: string;
  stage_id?: string;
  company_id?: string;
  lead_id?: string;
  owner_id?: string;
  description?: string;
  notes?: string;
}

export async function getOpportunities(params: GenericQueryParams = {}): Promise<OpportunityListResponse> {
  const { data } = await apiClient.get<OpportunityListResponse>('/opportunities', { params });
  return data;
}

export async function getOpportunity(id: string): Promise<Opportunity> {
  const { data } = await apiClient.get<Opportunity>(`/opportunities/${id}`);
  return data;
}

export async function createOpportunity(payload: CreateOpportunityData): Promise<Opportunity> {
  const { data } = await apiClient.post<Opportunity>('/opportunities', payload);
  return data;
}

export async function updateOpportunity(id: string, payload: Partial<CreateOpportunityData> & { stage_id?: string; status?: string }): Promise<Opportunity> {
  const { data } = await apiClient.put<Opportunity>(`/opportunities/${id}`, payload);
  return data;
}

export async function deleteOpportunity(id: string): Promise<void> {
  await apiClient.delete(`/opportunities/${id}`);
}
