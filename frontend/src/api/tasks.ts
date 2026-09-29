import apiClient from './client';
import { Task, TaskStatus } from '../types';

export interface CreateTaskData {
  title: string;
  description?: string;
  status?: string;
  priority?: string;
  due_date?: string;
  lead_id?: string;
  opportunity_id?: string;
  assigned_to_id?: string;
}

export async function getTasks(params: { status?: string; priority?: string; lead_id?: string; overdue_only?: boolean } = {}): Promise<Task[]> {
  const { data } = await apiClient.get<Task[]>('/tasks', { params });
  return data;
}

export async function getTask(id: string): Promise<Task> {
  const { data } = await apiClient.get<Task>(`/tasks/${id}`);
  return data;
}

export async function createTask(payload: CreateTaskData): Promise<Task> {
  const { data } = await apiClient.post<Task>('/tasks', payload);
  return data;
}

export async function updateTask(id: string, payload: Partial<CreateTaskData> & { status?: TaskStatus }): Promise<Task> {
  const { data } = await apiClient.put<Task>(`/tasks/${id}`, payload);
  return data;
}

export async function deleteTask(id: string): Promise<void> {
  await apiClient.delete(`/tasks/${id}`);
}
