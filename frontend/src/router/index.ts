import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../pages/LoginPage.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      redirect: '/upload',
    },
    {
      path: '/upload',
      name: 'Upload',
      component: () => import('../pages/UploadPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tasks',
      name: 'TaskList',
      component: () => import('../pages/TaskListPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tasks/:id',
      name: 'TaskDetail',
      component: () => import('../pages/TaskDetailPage.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/upload')
  } else {
    next()
  }
})

export default router
