<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTaskStore } from '../stores/taskStore'
import TaskStatusTag from '../components/TaskStatusTag.vue'

const router = useRouter()
const taskStore = useTaskStore()
const currentPage = ref(1)
const pageSize = ref(20)

onMounted(() => {
  loadTasks()
})

async function loadTasks() {
  await taskStore.fetchTasks(currentPage.value, pageSize.value)
}

function handlePageChange(page: number) {
  currentPage.value = page
  loadTasks()
}

function goToDetail(taskId: string) {
  router.push(`/tasks/${taskId}`)
}

function formatDate(dateStr: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<template>
  <div class="task-list-page">
    <el-card>
      <template #header>
        <div class="card-title">
          <el-icon size="20"><List /></el-icon>
          <span>识别任务列表</span>
        </div>
      </template>

      <el-table
        :data="taskStore.tasks"
        v-loading="taskStore.loading"
        stripe
        style="width: 100%"
        @row-click="(row: any) => goToDetail(row.id)"
        row-class-name="clickable-row"
      >
        <el-table-column prop="file_name" label="文件名" min-width="200" />
        <el-table-column prop="media_type" label="类型" width="80">
          <template #default>
            <el-tag size="small">图片</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <TaskStatusTag :status="row.status" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click.stop="goToDetail(row.id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination" v-if="taskStore.total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="taskStore.total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>

      <el-empty v-if="!taskStore.loading && taskStore.tasks.length === 0" description="暂无识别任务" />
    </el-card>
  </div>
</template>

<style scoped>
.task-list-page {
  max-width: 900px;
  margin: 0 auto;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

:deep(.clickable-row) {
  cursor: pointer;
}
</style>
