<template>
  <section class="page-stack">
    <header class="page-header">
      <div class="page-header__copy">
        <p class="page-header__eyebrow">Публичный курс</p>
        <h1 class="page-header__title">{{ detail?.title || 'Публичный курс' }}</h1>
      </div>

      <div class="page-header__actions">
        <RouterLink class="button button--secondary" to="/catalog">Назад в каталог</RouterLink>
        <button
          v-if="canRestrictPublicAccess"
          class="button button--secondary"
          type="button"
          :disabled="adminActionRunning"
          @click="restrictPublicAccess"
        >
          {{ adminActionRunning ? 'Обновляем...' : 'Убрать из общего доступа' }}
        </button>
        <button
          v-if="canBlockCreator"
          class="button button--danger"
          type="button"
          :disabled="adminActionRunning"
          @click="blockCreator"
        >
          {{ adminActionRunning ? 'Обновляем...' : 'Заблокировать пользователя' }}
        </button>
      </div>
    </header>

    <div v-if="error" class="notice notice--error">{{ error }}</div>
    <div v-if="success" class="notice notice--success">{{ success }}</div>
    <div v-else-if="loading" class="notice">Загружаем курс...</div>

    <template v-else-if="detail">
      <section class="screen-surface screen-surface--dark">
        <div class="screen-surface__body screen-hero">
          <div class="screen-hero__copy">
            <span class="pill">публичный курс</span>
            <h2 class="screen-hero__title">{{ detail.title }}</h2>
          </div>

          <div class="public-course-meta">
            <span class="pill">{{ formatDate(detail.created_at) }}</span>
            <strong>{{ mappedTopics.length }}</strong>
            <span>тем в структуре</span>
          </div>
        </div>
      </section>

      <section class="public-course-grid">
        <article class="card">
          <div class="card__body">
            <h2 class="public-course-title">Добавление к себе</h2>
            <p class="public-course-copy">
              После добавления курс появится в вашем списке, а тесты и прогресс будут полностью вашими.
            </p>

            <div v-if="!enrolled" class="public-course-enroll">
              <div class="field">
                <label class="field__label" for="initialDifficulty">Стартовая сложность</label>
                <select id="initialDifficulty" v-model.number="initialDifficulty" class="select">
                  <option :value="0">Базовая</option>
                  <option :value="1">Средняя</option>
                  <option :value="2">Продвинутая</option>
                </select>
              </div>

              <div class="actions">
                <button class="button" type="button" :disabled="enrolling || owned" @click="enroll">
                  {{ enrolling ? 'Добавляем...' : enrollButtonLabel }}
                </button>
              </div>
            </div>

            <div v-else class="notice notice--success">
              Курс уже есть в вашем списке.
            </div>

            <div v-if="owned" class="notice">
              Это ваш публичный курс. Его могут добавлять другие пользователи, но курс остается вашим.
            </div>
          </div>
        </article>

        <article class="card card--muted">
          <div class="card__body">
            <h2 class="public-course-title">Темы</h2>
            <TopicPopoverList :topics="mappedTopics" />
          </div>
        </article>

        <article class="card">
          <div class="card__body">
            <h2 class="public-course-title">Описание</h2>
            <p class="public-course-copy">{{ detail.comment || 'Описание курса пока не добавлено.' }}</p>
          </div>
        </article>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api, ApiError } from '@/api/client'
import type { DifficultyLevel, PublicCourseDetail } from '@/api/types'
import TopicPopoverList from '@/components/course/TopicPopoverList.vue'
import { useAuthStore } from '@/stores/auth'
import { mapTopics } from '@/utils/courseTopics'
import { formatDate } from '@/utils/format'

const props = defineProps<{ courseId: string }>()
const auth = useAuthStore()
const router = useRouter()

const loading = ref(false)
const enrolling = ref(false)
const adminActionRunning = ref(false)
const error = ref('')
const success = ref('')
const detail = ref<PublicCourseDetail | null>(null)
const enrolled = ref(false)
const owned = ref(false)
const initialDifficulty = ref<DifficultyLevel>(0)

const courseId = computed(() => Number(props.courseId))
const isAdmin = computed(() => auth.currentUser?.role === 'admin')
const isAuthenticated = computed(() => auth.isAuthenticated)
const canRestrictPublicAccess = computed(() => isAdmin.value && !owned.value && Boolean(detail.value?.is_public))
const canBlockCreator = computed(() => isAdmin.value && !owned.value && Boolean(detail.value?.creator_id))
const mappedTopics = computed(() => (detail.value ? mapTopics(detail.value.topics) : []))
const enrollButtonLabel = computed(() => {
  return isAuthenticated.value ? 'Добавить себе' : 'Войти и добавить'
})

async function loadMembership() {
  if (!isAuthenticated.value) {
    enrolled.value = false
    owned.value = false
    return
  }

  try {
    const membership = await api.getCourseMembership(courseId.value)
    enrolled.value = membership.enrolled
    owned.value = membership.owned
  } catch {
    enrolled.value = false
    owned.value = false
  }
}

async function loadDetail() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    const [course] = await Promise.all([
      api.getPublicCourseDetail(courseId.value),
      loadMembership(),
    ])
    detail.value = course
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось загрузить публичный курс.'
  } finally {
    loading.value = false
  }
}

async function enroll() {
  if (!isAuthenticated.value) {
    await router.push({ name: 'login', query: { next: router.currentRoute.value.fullPath } })
    return
  }

  enrolling.value = true
  error.value = ''
  success.value = ''
  try {
    await api.enrollPublicCourse(courseId.value, {
      initial_difficulty: initialDifficulty.value,
    })
    enrolled.value = true
    await router.push({ name: 'course-detail', params: { courseId: courseId.value } })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось добавить курс.'
  } finally {
    enrolling.value = false
  }
}

async function restrictPublicAccess() {
  if (!detail.value) {
    return
  }

  adminActionRunning.value = true
  error.value = ''
  success.value = ''
  try {
    await api.adminRestrictCoursePublicAccess(courseId.value)
    success.value = 'Курс снят с общего доступа.'
    await router.replace({ name: 'catalog' })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось снять курс с общего доступа.'
  } finally {
    adminActionRunning.value = false
  }
}

async function blockCreator() {
  const creatorId = detail.value?.creator_id
  if (!creatorId) {
    return
  }

  if (!window.confirm('Заблокировать владельца этого курса?')) {
    return
  }

  adminActionRunning.value = true
  error.value = ''
  success.value = ''
  try {
    await api.adminBlockUser(creatorId)
    success.value = 'Пользователь заблокирован.'
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось заблокировать пользователя.'
  } finally {
    adminActionRunning.value = false
  }
}

onMounted(loadDetail)
</script>

<style scoped>
.public-course-meta {
  min-width: 180px;
  display: grid;
  gap: 8px;
  justify-items: end;
  text-align: right;
}

.public-course-meta strong {
  font-size: 58px;
  line-height: 0.95;
}

.public-course-meta span:last-child {
  color: rgba(255, 255, 255, 0.72);
}

.public-course-grid {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: 18px;
}

.public-course-title {
  margin: 0 0 16px;
  font-size: 24px;
}

.public-course-copy {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}

.public-course-enroll {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

@media (max-width: 1100px) {
  .public-course-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .public-course-meta {
    justify-items: start;
    text-align: left;
  }
}
</style>
