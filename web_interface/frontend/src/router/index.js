import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/constellation',
      name: 'constellation-designer',
      component: () => import('@/views/ConstellationDesigner.vue')
    },
    {
      path: '/planning',
      name: 'planning',
      component: () => import('@/views/Planning.vue')
    },
    {
      path: '/results',
      name: 'results',
      component: () => import('@/views/Results.vue')
    }
  ]
})

export default router
