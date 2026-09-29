import apiClient from './client';
import { Contact } from '../types';

export interface CreateContactData {
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  job_title?: string;
  company_id?: string;
  linkedin_url?: string;
  notes?: string;
}

export async function getContacts(params: { search?: string } = {}): Promise<Contact[]> {
  const { data } = await apiClient.get<Contact[]>('/contacts', { params });
  return data;
}

export async function getContact(id: string): Promise<Contact> {
  const { data } = await apiClient.get<Contact>(`/contacts/${id}`);
  return data;
}

export async function createContact(payload: CreateContactData): Promise<Contact> {
  const { data } = await apiClient.post<Contact>('/contacts', payload);
  return data;
}

export async function updateContact(id: string, payload: Partial<CreateContactData>): Promise<Contact> {
  const { data } = await apiClient.put<Contact>(`/contacts/${id}`, payload);
  return data;
}

export async function deleteContact(id: string): Promise<void> {
  await apiClient.delete(`/contacts/${id}`);
}
