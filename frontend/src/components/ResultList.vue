<script setup lang="ts">
import type { ClassificationItem } from '../types/detection'

defineProps<{
  items: ClassificationItem[]
}>()

function formatScore(score: number): string {
  return (score * 100).toFixed(2) + '%'
}

function getScoreColor(score: number): string {
  if (score >= 0.7) return '#67c23a'
  if (score >= 0.4) return '#e6a23c'
  return '#909399'
}
</script>

<template>
  <div class="result-list">
    <el-table :data="items" stripe style="width: 100%">
      <el-table-column type="index" label="#" width="50" />
      <el-table-column prop="keyword" label="识别关键词" min-width="150">
        <template #default="{ row }">
          <el-text tag="b">{{ row.keyword }}</el-text>
        </template>
      </el-table-column>
      <el-table-column prop="root" label="类别" min-width="180" />
      <el-table-column prop="score" label="置信度" width="120">
        <template #default="{ row }">
          <el-text :style="{ color: getScoreColor(row.score), fontWeight: '600' }">
            {{ formatScore(row.score) }}
          </el-text>
        </template>
      </el-table-column>
      <el-table-column label="置信度条" width="150">
        <template #default="{ row }">
          <el-progress
            :percentage="Math.round(row.score * 100)"
            :stroke-width="10"
            :color="getScoreColor(row.score)"
            :show-text="false"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.result-list {
  margin-top: 8px;
}
</style>
