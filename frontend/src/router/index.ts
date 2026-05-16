import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/courses',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/courses',
      name: 'courses',
      component: () => import('@/views/CoursesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/catalog',
      name: 'catalog',
      component: () => import('@/views/CatalogView.vue'),
    },
    {
      path: '/catalog/:courseId',
      name: 'catalog-course',
      component: () => import('@/views/PublicCourseDetailView.vue'),
      props: true,
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/courses/new',
      name: 'course-create',
      component: () => import('@/views/CourseCreateView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/courses/:courseId',
      name: 'course-detail',
      component: () => import('@/views/CourseDetailView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/courses/:courseId/tests/:testId',
      name: 'course-test',
      component: () => import('@/views/CourseTestView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/courses/:courseId/tests/:testId/review',
      name: 'course-test-review',
      component: () => import('@/views/TestReviewView.vue'),
      meta: { requiresAuth: true },
      props: true,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.ready) {
    await auth.bootstrap()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { next: to.fullPath } }
  }

  if (to.meta.requiresAdmin && auth.currentUser?.role !== 'admin') {
    return { name: 'courses' }
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'courses' }
  }

  return true
})

export default router
