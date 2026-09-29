import apiClient from './client';
import { Pipeline } from '../types';

export async function getPipelines(): Promise<Pipeline[]> {
  const { data } = await apiClient.get<Pipeline[]>('/pipelines');
  return data;
}

export async function getPipeline(id: number): Promise<Pipeline> {
  const { data } = await apiClient.get<Pipeline>(`/pipelines/${id}`);
  return data;
}
