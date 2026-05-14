<template>
  <section class="stack">
    <div class="split">
      <p class="hero__text">Здесь собраны пользователи и курсы, доступ к которым ограничил администратор.</p>
      <button class="button button--secondary" type="button" @click="reload" :disabled="loading">
        {{ loading ? 'Обновляем...' : 'Обновить' }}
      </button>
    </div>

    <div v-if="error" class="notice notice--error">{{ error }}</div>
    <div v-if="success" class="notice notice--success">{{ success }}</div>

    <div class="grid grid--2 admin-grid">
      <section class="card">
        <div class="card__body stack">
          <div class="split">
            <h2 class="section-title">Заблокированные пользователи</h2>
            <span class="pill">{{ blockedMeta.total }}</span>
          </div>

          <div v-if="blockedUsers.length === 0" class="empty">
            Заблокированных пользователей нет.
          </div>

          <article v-for="user in blockedUsers" :key="user.id" class="admin-row">
            <div>
              <h3 class="admin-row__title">{{ user.username }}</h3>
              <p class="admin-row__meta">{{ user.email }}</p>
            </div>
            <button class="button button--secondary" type="button" @click="unblockUser(user.id)" :disabled="busy">
              Разблокировать
            </button>
          </article>

          <PaginationControls
            v-if="blockedMeta.total > blockedMeta.limit"
            :total="blockedMeta.total"
            :limit="blockedMeta.limit"
            :offset="blockedMeta.offset"
            :loading="loading"
            @prev="prevBlockedPage"
            @next="nextBlockedPage"
          />
        </div>
      </section>

      <section class="card">
        <div class="card__body stack">
          <div class="split">
            <h2 class="section-title">Снятые с общего доступа</h2>
            <span class="pill">{{ restrictedMeta.total }}</span>
          </div>

          <div v-if="restrictedCourses.length === 0" class="empty">
            Ограниченных курсов нет.
          </div>

          <article v-for="course in restrictedCourses" :key="course.id" class="admin-row">
            <RouterLink class="admin-row__link" :to="`/courses/${course.id}`">
              <h3 class="admin-row__title">{{ course.title }}</h3>
              <p class="admin-row__meta">{{ course.creator_username }} · {{ course.creator_email }}</p>
            </RouterLink>
            <button class="button button--secondary" type="button" @click="restoreCourse(course.id)" :disabled="busy">
              Вернуть в общий доступ
            </button>
          </article>

          <PaginationControls
            v-if="restrictedMeta.total > restrictedMeta.limit"
            :total="restrictedMeta.total"
            :limit="restrictedMeta.limit"
            :offset="restrictedMeta.offset"
            :loading="loading"
            @prev="prevRestrictedPage"
            @next="nextRestrictedPage"
          />
        </div>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api, ApiError } from '@/api/client'
import type { AdminCourse, AdminUser, PaginationMeta } from '@/api/types'
import PaginationControls from '@/components/ui/PaginationControls.vue'

const PAGE_LIMIT = 10

const blockedUsers = ref<AdminUser[]>([])
const restrictedCourses = ref<AdminCourse[]>([])
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const success = ref('')
const blockedMeta = reactive<PaginationMeta>({
  total: 0,
  limit: PAGE_LIMIT,
  offset: 0,
})
const restrictedMeta = reactive<PaginationMeta>({
  total: 0,
  limit: PAGE_LIMIT,
  offset: 0,
})

async function loadBlockedUsers() {
  const response = await api.getBlockedUsers(blockedMeta.limit, blockedMeta.offset)
  blockedUsers.value = response.items
  blockedMeta.total = response.meta.total
  blockedMeta.limit = response.meta.limit
  blockedMeta.offset = response.meta.offset
}

async function loadRestrictedCourses() {
  const response = await api.getRestrictedCourses(restrictedMeta.limit, restrictedMeta.offset)
  restrictedCourses.value = response.items
  restrictedMeta.total = response.meta.total
  restrictedMeta.limit = response.meta.limit
  restrictedMeta.offset = response.meta.offset
}

async function reload() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadBlockedUsers(), loadRestrictedCourses()])
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось загрузить админ-панель.'
  } finally {
    loading.value = false
  }
}

function nextBlockedPage() {
  blockedMeta.offset += blockedMeta.limit
  void loadBlockedUsers()
}

function prevBlockedPage() {
  blockedMeta.offset = Math.max(0, blockedMeta.offset - blockedMeta.limit)
  void loadBlockedUsers()
}

function nextRestrictedPage() {
  restrictedMeta.offset += restrictedMeta.limit
  void loadRestrictedCourses()
}

function prevRestrictedPage() {
  restrictedMeta.offset = Math.max(0, restrictedMeta.offset - restrictedMeta.limit)
  void loadRestrictedCourses()
}

async function unblockUser(userId: number) {
  busy.value = true
  error.value = ''
  success.value = ''
  try {
    await api.adminUnblockUser(userId)
    success.value = 'Пользователь разблокирован.'
    await loadBlockedUsers()
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось разблокировать пользователя.'
  } finally {
    busy.value = false
  }
}

async function restoreCourse(courseId: number) {
  busy.value = true
  error.value = ''
  success.value = ''
  try {
    await api.adminRestoreCoursePublicAccess(courseId)
    success.value = 'Курс возвращен в общий доступ.'
    await loadRestrictedCourses()
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось вернуть курс в общий доступ.'
  } finally {
    busy.value = false
  }
}

onMounted(reload)
</script>
