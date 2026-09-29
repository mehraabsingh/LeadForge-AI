import apiClient from './client';
import { DashboardStats, DashboardCharts } from '../types';

export async function getStats(): Promise<DashboardStats> {
  const { data } = await apiClient.get<DashboardStats>('/dashboard/stats');
  return data;
}

export async function getCharts(): Promise<DashboardCharts> {
  const { data } = await apiClient.get<DashboardCharts>('/dashboard/charts');
  return data;
}
