export interface ClassificationItem {
  keyword: string
  root: string
  score: number
}

export interface DetectionResult {
  task_id: string
  result_num: number
  items: ClassificationItem[]
  raw_log_id: string | null
}

export type TaskStatus = 'pending' | 'processing' | 'success' | 'failed'

export interface TaskBrief {
  id: string
  file_name: string
  media_type: string
  status: TaskStatus
  created_at: string
  updated_at: string
}

export interface TaskListResponse {
  items: TaskBrief[]
  page: number
  page_size: number
  total: number
}

export interface TaskDetail {
  id: string
  user_id: string
  file_name: string
  media_type: string
  status: TaskStatus
  created_at: string
  updated_at: string
  original_file_url: string | null
  result_file_url: string | null
  error_message: string | null
}

export interface TaskDetailResponse {
  task: TaskDetail
  result: DetectionResult | null
}
