import apiClient from './request'
import type { TaskListResponse, TaskDetailResponse } from '../types/detection'

export function createTask(file: File): Promise<{ id: string; status: string; media_type: string }> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('media_type', 'image')
  return apiClient
    .post('/api/tasks', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    .then((res) => res.data)
}

export function getTaskList(
  page: number = 1,
  pageSize: number = 20,
  status?: string
): Promise<TaskListResponse> {
  const params: Record<string, string | number> = { page, page_size: pageSize }
  if (status) params.status = status
  return apiClient.get('/api/tasks', { params }).then((res) => res.data)
}

export function getTaskDetail(taskId: string): Promise<TaskDetailResponse> {
  return apiClient.get(`/api/tasks/${taskId}`).then((res) => res.data)
}
