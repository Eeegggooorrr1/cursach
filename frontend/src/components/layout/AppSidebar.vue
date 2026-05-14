<template>
  <aside class="rail">
    <nav class="rail__nav" aria-label="Основная навигация">
      <component
        :is="item.requiresAuth && !auth.currentUser ? 'button' : RouterLink"
        v-for="item in navItems"
        :key="item.to"
        class="rail__item"
        :class="{ 'rail__item--active': isActive(item.to) }"
        :to="item.requiresAuth && !auth.currentUser ? undefined : item.to"
        :type="item.requiresAuth && !auth.currentUser ? 'button' : undefined"
        :title="item.label"
        :aria-label="item.label"
        @click="handleItemClick(item)"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            :d="item.icon"
            fill="none"
            stroke="currentColor"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.8"
          />
        </svg>
      </component>
    </nav>

    <Transition name="auth-gate">
      <div v-if="guestPromptOpen" class="auth-gate" @click.self="closeGuestPrompt">
        <div class="auth-gate__backdrop"></div>
        <div class="auth-gate__dialog card">
          <div class="card__body auth-gate__body">
            <span class="pill">Нужен аккаунт</span>
            <h2>Этот раздел откроется после входа</h2>
            <div class="actions">
              <button class="button" type="button" @click="goToAuth('login')">Войти</button>
              <button class="button button--secondary" type="button" @click="goToAuth('register')">
                Регистрация
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

type NavItem = {
  to: string
  label: string
  icon: string
  requiresAuth: boolean
}

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const guestPromptOpen = ref(false)
const pendingPath = ref('/courses')

const navItems = computed<NavItem[]>(() => {
  const items: NavItem[] = [
    {
      to: '/courses',
      label: 'Курсы',
      icon: 'M3 12.5 12 4l9 8.5M5 10.7V20h14v-9.3',
      requiresAuth: true,
    },
    {
      to: '/catalog',
      label: 'Каталог',
      icon: 'M11 19a8 8 0 1 1 5.3-14M21 21l-4.35-4.35',
      requiresAuth: false,
    },
    {
      to: '/courses/new',
      label: 'Новый курс',
      icon: 'M12 5v14M5 12h14',
      requiresAuth: true,
    },
    {
      to: '/profile',
      label: 'Профиль',
      icon: 'M20 21a8 8 0 0 0-16 0M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8',
      requiresAuth: true,
    },
  ]

  if (auth.currentUser?.role === 'admin') {
    items.splice(3, 0, {
      to: '/admin',
      label: 'Админ',
      icon: 'M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3Zm0 5v8m-3-4h6',
      requiresAuth: true,
    })
  }

  return items
})

function handleItemClick(item: NavItem) {
  if (!item.requiresAuth || auth.currentUser) {
    return
  }

  pendingPath.value = item.to
  guestPromptOpen.value = true
}

function closeGuestPrompt() {
  guestPromptOpen.value = false
}

function goToAuth(target: 'login' | 'register') {
  guestPromptOpen.value = false
  router.push({ name: target, query: { next: pendingPath.value } })
}

function isActive(path: string) {
  if (path === '/courses') {
    return route.path.startsWith('/courses') && !route.path.startsWith('/courses/new')
  }
  if (path === '/courses/new') {
    return route.path.startsWith('/courses/new')
  }
  if (path === '/catalog') {
    return route.path.startsWith('/catalog')
  }
  if (path === '/profile') {
    return route.path.startsWith('/profile')
  }
  if (path === '/admin') {
    return route.path.startsWith('/admin')
  }
  return route.path.startsWith(path)
}
</script>

<style scoped>
.rail {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 28px;
  padding: 20px 14px;
  color: white;
  background: #111827;
}

.rail__nav {
  display: grid;
  gap: 12px;
}

.rail__item {
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 16px;
  color: rgba(255, 255, 255, 0.74);
  background: rgba(255, 255, 255, 0.08);
  cursor: pointer;
  font: inherit;
  transition: 180ms ease;
}

.rail__item:hover,
.rail__item--active {
  color: #111827;
  background: white;
  transform: translateY(-2px);
}

.rail__item svg {
  width: 20px;
  height: 20px;
}

.auth-gate {
  position: fixed;
  inset: 0;
  z-index: 30;
  display: grid;
  place-items: center;
  padding: 24px;
}

.auth-gate__backdrop {
  position: absolute;
  inset: 0;
  backdrop-filter: blur(14px);
  background: rgba(17, 24, 39, 0.34);
}

.auth-gate__dialog {
  position: relative;
  width: min(460px, calc(100vw - 32px));
  border-radius: 28px;
  box-shadow: 0 32px 70px rgba(17, 24, 39, 0.24);
}

.auth-gate__body {
  display: grid;
  gap: 18px;
}

.auth-gate__body h2 {
  margin: 0;
  color: var(--text);
  font-size: 28px;
  line-height: 1.1;
}

.auth-gate-enter-active,
.auth-gate-leave-active {
  transition: opacity 180ms ease, transform 180ms ease;
}

.auth-gate-enter-from,
.auth-gate-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

@media (max-width: 900px) {
  .rail {
    position: static;
    height: auto;
    flex-direction: row;
    gap: 16px;
    padding: 14px;
  }

  .rail__nav {
    display: flex;
    flex-wrap: wrap;
  }
}
</style>
