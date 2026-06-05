<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/authStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLoggedIn = computed(() => authStore.isLoggedIn)
const showNav = computed(() => route.path !== '/login')

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="app-container">
    <el-header v-if="showNav" class="app-header">
      <div class="header-content">
        <div class="logo" @click="router.push('/upload')">
          <el-icon size="24"><PictureFilled /></el-icon>
          <span>物体识别系统</span>
        </div>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="route.path"
          class="nav-menu"
        >
          <el-menu-item index="/upload">
            <el-icon><UploadFilled /></el-icon>
            上传识别
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><List /></el-icon>
            任务列表
          </el-menu-item>
        </el-menu>
        <div class="user-info" v-if="isLoggedIn">
          <span class="username">{{ authStore.user?.username }}</span>
          <el-button type="danger" text @click="handleLogout">退出</el-button>
        </div>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.app-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0 24px;
  height: 60px;
  line-height: 60px;
}

.header-content {
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
  cursor: pointer;
  margin-right: 40px;
}

.nav-menu {
  flex: 1;
  border-bottom: none;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  color: #606266;
  font-size: 14px;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 24px;
}
</style>
