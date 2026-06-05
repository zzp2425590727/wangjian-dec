<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createTask } from '../api/taskApi'
import { ElMessage } from 'element-plus'
import type { UploadProps } from 'element-plus'

const router = useRouter()
const uploading = ref(false)

const beforeUpload: UploadProps['beforeUpload'] = (file: File) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 JPG、PNG、WebP 格式的图片')
    return false
  }
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  uploading.value = true
  return true
}

async function handleUpload(options: { file: File }) {
  try {
    const res = await createTask(options.file)
    ElMessage.success('上传成功，正在识别...')
    router.push(`/tasks/${res.id}`)
  } catch {
    // Error handled by interceptor
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="upload-page">
    <el-card class="upload-card">
      <template #header>
        <div class="card-title">
          <el-icon size="20"><UploadFilled /></el-icon>
          <span>上传图片进行识别</span>
        </div>
      </template>
      <el-upload
        drag
        :show-file-list="false"
        :before-upload="beforeUpload"
        :http-request="handleUpload"
        accept=".jpg,.jpeg,.png,.webp"
        class="upload-area"
      >
        <div v-if="uploading" class="uploading-state">
          <el-icon class="is-loading" size="48"><Loading /></el-icon>
          <p>正在上传并识别中...</p>
        </div>
        <div v-else>
          <el-icon size="48" color="#c0c4cc"><UploadFilled /></el-icon>
          <p>将图片拖到此处，或<em>点击上传</em></p>
          <p class="upload-tip">支持 JPG、PNG、WebP 格式，最大 10MB</p>
        </div>
      </el-upload>
    </el-card>
  </div>
</template>

<style scoped>
.upload-page {
  display: flex;
  justify-content: center;
  padding-top: 60px;
}

.upload-card {
  width: 600px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-area p {
  margin: 8px 0 0;
  color: #606266;
}

.upload-area em {
  color: #409eff;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399 !important;
}

.uploading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
</style>
