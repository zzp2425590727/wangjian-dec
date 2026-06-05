import apiClient from './request'
import type { LoginRequest, LoginResponse, UserInfo } from '../types/auth'

export function login(data: LoginRequest): Promise<LoginResponse> {
  return apiClient.post('/api/auth/login', data).then((res) => res.data)
}

export function getCurrentUser(): Promise<UserInfo> {
  return apiClient.get('/api/auth/me').then((res) => res.data)
}
