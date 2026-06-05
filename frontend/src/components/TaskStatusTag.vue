<script setup lang="ts">
import type { TaskStatus } from '../types/detection'

const props = defineProps<{
  status: TaskStatus
}>()

const statusMap: Record<TaskStatus, { label: string; type: string }> = {
  pending: { label: '等待处理', type: 'info' },
  processing: { label: '处理中', type: 'warning' },
  success: { label: '识别成功', type: 'success' },
  failed: { label: '识别失败', type: 'danger' },
}

const statusInfo = statusMap[props.status] || { label: '未知', type: 'info' }
</script>

<template>
  <el-tag :type="statusInfo.type as any" size="small">
    {{ statusInfo.label }}
  </el-tag>
</template>
