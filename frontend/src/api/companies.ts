import apiClient from './client';
import { Company, Contact, Activity } from '../types';

export interface CreateCompanyData {
  name: string;
  industry?: string;
  size?: string;
  location?: string;
  website?: string;
  phone?: string;
  email?: string;
  description?: string;
  annual_revenue?: number;
}

export async function getCompanies(params: { search?: string } = {}): Promise<Company[]> {
  const { data } = await apiClient.get<Company[]>('/companies', { params });
  return data;
}

export async function getCompany(id: string): Promise<Company> {
  const { data } = await apiClient.get<Company>(`/companies/${id}`);
  return data;
}

export async function createCompany(payload: CreateCompanyData): Promise<Company> {
  const { data } = await apiClient.post<Company>('/companies', payload);
  return data;
}

export async function updateCompany(id: string, payload: Partial<CreateCompanyData>): Promise<Company> {
  const { data } = await apiClient.put<Company>(`/companies/${id}`, payload);
  return data;
}

export async function deleteCompany(id: string): Promise<void> {
  await apiClient.delete(`/companies/${id}`);
}

export async function getCompanyContacts(id: string): Promise<Contact[]> {
  const { data } = await apiClient.get<Contact[]>(`/companies/${id}/contacts`);
  return data;
}

export async function getCompanyActivities(id: string): Promise<Activity[]> {
  const { data } = await apiClient.get<Activity[]>(`/companies/${id}/activities`);
  return data;
}
