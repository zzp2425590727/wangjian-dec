<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTaskStore } from '../stores/taskStore'
import TaskStatusTag from '../components/TaskStatusTag.vue'
import ResultList from '../components/ResultList.vue'
import type { TaskDetailResponse } from '../types/detection'

const route = useRoute()
const taskStore = useTaskStore()
const taskData = ref<TaskDetailResponse | null>(null)
const pollTimer = ref<number | null>(null)
const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

onMounted(async () => {
  const taskId = route.params.id as string
  await loadTask(taskId)
})

onUnmounted(() => {
  stopPolling()
})

async function loadTask(taskId: string) {
  const res = await taskStore.fetchTaskDetail(taskId)
  taskData.value = res

  if (res.task.status === 'pending' || res.task.status === 'processing') {
    startPolling(taskId)
  }
}

function startPolling(taskId: string) {
  stopPolling()
  pollTimer.value = window.setInterval(async () => {
    try {
      const res = await taskStore.fetchTaskDetail(taskId)
      taskData.value = res
      if (res.task.status === 'success' || res.task.status === 'failed') {
        stopPolling()
      }
    } catch {
      stopPolling()
    }
  }, 2000)
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function getImageUrl(taskId: string) {
  const token = localStorage.getItem('access_token')
  return `${baseUrl}/api/files/${taskId}/original/raw?token=${token}`
}
</script>

<template>
  <div class="task-detail-page">
    <el-card v-if="taskData" class="detail-card">
      <template #header>
        <div class="card-title">
          <el-icon size="20"><Document /></el-icon>
          <span>任务详情</span>
          <TaskStatusTag :status="taskData.task.status" style="margin-left: auto" />
        </div>
      </template>

      <el-descriptions :column="2" border class="task-info">
        <el-descriptions-item label="任务ID">{{ taskData.task.id }}</el-descriptions-item>
        <el-descriptions-item label="文件名">{{ taskData.task.file_name }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag size="small">{{ taskData.task.media_type === 'image' ? '图片' : taskData.task.media_type }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(taskData.task.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(taskData.task.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <TaskStatusTag :status="taskData.task.status" />
        </el-descriptions-item>
      </el-descriptions>

      <el-alert
        v-if="taskData.task.status === 'failed' && taskData.task.error_message"
        :title="'识别失败: ' + taskData.task.error_message"
        type="error"
        show-icon
        :closable="false"
        style="margin-top: 16px"
      />

      <div v-if="taskData.task.status === 'pending' || taskData.task.status === 'processing'" class="loading-state">
        <el-icon class="is-loading" size="32"><Loading /></el-icon>
        <p>正在识别中，请稍候...</p>
      </div>

      <div v-if="taskData.task.original_file_url" class="image-section">
        <h3>原始图片</h3>
        <div class="image-container">
          <el-image
            :src="getImageUrl(taskData.task.id)"
            fit="contain"
            class="preview-image"
            :preview-src-list="[getImageUrl(taskData.task.id)]"
          >
            <template #error>
              <div class="image-error">
                <el-icon size="32"><PictureFilled /></el-icon>
                <p>图片加载失败</p>
              </div>
            </template>
          </el-image>
        </div>
      </div>

      <div v-if="taskData.result && taskData.result.items.length > 0" class="result-section">
        <h3>识别结果</h3>
        <ResultList :items="taskData.result.items" />
      </div>
    </el-card>

    <div v-else v-loading="true" class="loading-container"></div>
  </div>
</template>

<style scoped>
.task-detail-page {
  max-width: 800px;
  margin: 0 auto;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.task-info {
  margin-bottom: 16px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 0;
  color: #909399;
}

.image-section,
.result-section {
  margin-top: 24px;
}

.image-section h3,
.result-section h3 {
  margin: 0 0 12px;
  font-size: 15px;
  color: #303133;
}

.image-container {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: #fafafa;
}

.preview-image {
  width: 100%;
  max-height: 400px;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px;
  color: #c0c4cc;
}

.loading-container {
  height: 400px;
}
</style>
