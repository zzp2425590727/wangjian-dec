import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TaskBrief, TaskDetailResponse } from '../types/detection'
import { getTaskList, getTaskDetail } from '../api/taskApi'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<TaskBrief[]>([])
  const total = ref(0)
  const currentTask = ref<TaskDetailResponse | null>(null)
  const loading = ref(false)

  async function fetchTasks(page: number = 1, pageSize: number = 20, status?: string) {
    loading.value = true
    try {
      const res = await getTaskList(page, pageSize, status)
      tasks.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchTaskDetail(taskId: string) {
    loading.value = true
    try {
      const res = await getTaskDetail(taskId)
      currentTask.value = res
      return res
    } finally {
      loading.value = false
    }
  }

  return { tasks, total, currentTask, loading, fetchTasks, fetchTaskDetail }
})
