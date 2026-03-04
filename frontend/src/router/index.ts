import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@/views/ProjectsView.vue')
    },
    {
      path: '/projects/:id',
      name: 'project',
      component: () => import('@/views/ProjectView.vue')
    },
    {
      path: '/projects/:id/edit',
      name: 'edit',
      component: () => import('@/views/EditView.vue')
    }
  ]
})

export default router