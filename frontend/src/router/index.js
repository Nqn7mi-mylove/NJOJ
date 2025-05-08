import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import store from '../store'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/problems',
    name: 'problems',
    component: () => import('../views/ProblemListView.vue')
  },
  {
    path: '/problems/:id',
    name: 'problem-detail',
    component: () => import('../views/ProblemDetailView.vue')
  },
  {
    path: '/submissions',
    name: 'submissions',
    component: () => import('../views/SubmissionListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/submissions/:id',
    name: 'submission-detail',
    component: () => import('../views/SubmissionDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/signup',
    name: 'signup',
    component: () => import('../views/SignupView.vue'),
    meta: { guestOnly: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/admin/AdminDashboardView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/problems',
    name: 'admin-problems',
    component: () => import('../views/admin/ProblemManagementView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/problems/create',
    name: 'admin-problem-create',
    component: () => import('../views/admin/ProblemEditView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/problems/:id/edit',
    name: 'admin-problem-edit',
    component: () => import('../views/admin/ProblemEditView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/settings',
    name: 'admin-settings',
    component: () => import('../views/admin/SystemSettingsView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isLoggedIn = store.getters['auth/isLoggedIn']
  const isAdmin = store.getters['auth/isAdmin']

  // Check if route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
      // If route requires admin role but user is not admin
      next({ path: '/' })
    } else {
      next()
    }
  } 
  // Check if route is for guests only (login, signup)
  else if (to.matched.some(record => record.meta.guestOnly)) {
    if (isLoggedIn) {
      next({ path: '/' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
