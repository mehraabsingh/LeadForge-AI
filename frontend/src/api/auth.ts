import apiClient from './client';
import { User } from '../types';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface UpdateMeRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  current_password?: string;
  new_password?: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/auth/login', { email, password });
  return data;
}

export async function register(payload: RegisterRequest): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/auth/register', payload);
  return data;
}

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me');
  return data;
}

export async function updateMe(payload: UpdateMeRequest): Promise<User> {
  const { data } = await apiClient.put<User>('/auth/me', payload);
  return data;
}

export async function getUsers(): Promise<{ users: User[]; total: number }> {
  const { data } = await apiClient.get<{ users: User[]; total: number }>('/users');
  return data;
}

export async function updateUserRole(userId: string, role: string): Promise<User> {
  const { data } = await apiClient.put<User>(`/users/${userId}`, { role });
  return data;
}
