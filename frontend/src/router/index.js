import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/admin-login',
      name: 'admin-login',
      component: () => import('../views/AdminLoginView.vue')
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/card-usage',
      name: 'card-usage',
      component: () => import('../views/CardUsageView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/card-usage-summary',
      name: 'card-usage-summary',
      component: () => import('../views/CardUsageSummaryView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/budget',
      name: 'budget',
      component: () => import('../views/BudgetView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/notices',
      name: 'notices',
      component: () => import('../views/NoticeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/contacts',
      name: 'contacts',
      component: () => import('../views/ContactView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 1. 인증이 필요한 페이지인데 토큰이 없는 경우 -> 로그인 페이지로 이동
  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login' })
  } 
  
  // 2. 이미 로그인된 상태에서 로그인 관련 페이지 접근 시 (뒤로가기 포함)
  // 현재 페이지에 머물거나 홈으로 이동하여 세션 유지
  if ((to.name === 'login' || to.name === 'admin-login') && token) {
    if (from.path !== '/' && from.name) {
      // 이전 페이지가 있고 홈이 아니라면 그 페이지 유지 시도 (뒤로가기 차단)
      return next(false) 
    }
    // 기본적으로 홈으로 리다이렉트
    return next({ name: 'home' })
  }

  // 3. 그 외의 경우 정상 이동
  next()
})

export default router
