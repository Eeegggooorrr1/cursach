<template>
  <section class="page-stack">
    <header class="page-header">
      <div class="page-header__copy">
        <p class="page-header__eyebrow">Курс</p>
        <h1 class="page-header__title">{{ detail?.course.title || 'Курс' }}</h1>
      </div>

      <div class="page-header__actions">
        <button
          v-if="isCreator"
          class="button button--secondary"
          type="button"
          :disabled="visibilityUpdating"
          @click="toggleVisibility"
        >
          {{ visibilityUpdating ? 'Обновляем...' : visibilityActionLabel }}
        </button>
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
        <button v-if="canUseLearningActions" class="button" type="button" :disabled="generateTestDisabled" @click="generateTest">
          {{ generateTestButtonLabel }}
        </button>
        <button v-if="canUseLearningActions" class="button button--danger" type="button" :disabled="deleting" @click="deleteCourse">
          {{ deleting ? 'Удаляем...' : deleteActionLabel }}
        </button>
      </div>
    </header>

    <div v-if="error" class="notice notice--error">{{ error }}</div>
    <div v-if="success" class="notice notice--success">{{ success }}</div>
    <div v-if="loading && !detail" class="notice">Загружаем курс...</div>

    <template v-if="detail">
      <section class="screen-surface screen-surface--dark">
        <div class="screen-surface__body screen-hero">
          <div class="screen-hero__copy">
            <span class="pill">{{ detail.course.is_public ? 'публичный курс' : 'приватный курс' }}</span>
            <h2 class="screen-hero__title">{{ detail.course.title }}</h2>
          </div>
          <div class="course-scoreboard">
            <span class="pill">{{ formatDate(detail.course.created_at) }}</span>
            <strong>{{ detail.tests.length }}</strong>
            <span>тестов в истории</span>
          </div>
        </div>
      </section>

      <section class="course-detail-grid">
        <article class="card course-detail-grid__history">
          <div class="card__body">
            <div class="split">
              <h2 class="course-section-title">История тестов</h2>
              <span class="pill">{{ detail.tests.length }}</span>
            </div>

            <div v-if="detail.tests.length === 0" class="empty-state course-detail-empty">
              Здесь пока нет тестов. Создайте первый тест, и история появится в этом блоке.
            </div>

            <div v-else class="course-history-list">
              <template v-for="test in detail.tests" :key="test.id">
                <RouterLink
                  v-if="testActionLink(test.id, test.status)"
                  :to="testActionLink(test.id, test.status)!"
                  class="course-history-item"
                >
                  <div class="course-history-item__head">
                    <div>
                      <h3>{{ test.title }}</h3>
                      <p>Попытка {{ test.position }}</p>
                    </div>
                    <span class="pill" :class="statusTone(test.status)">{{ formatStatusLabel(test.status) }}</span>
                  </div>
                  <div class="course-history-item__stats">
                    <span>Верно: {{ formatPercent(test.correct_percentage) }}</span>
                    <span>Ошибки: {{ formatPercent(test.error_percentage) }}</span>
                  </div>
                  <div class="course-history-item__foot">
                    <span>{{ formatDate(test.started_at) }}</span>
                    <span>{{ testActionLabel(test.status) }}</span>
                  </div>
                </RouterLink>

                <article v-else class="course-history-item course-history-item--disabled">
                  <div class="course-history-item__head">
                    <div>
                      <h3>{{ test.title }}</h3>
                      <p>Попытка {{ test.position }}</p>
                    </div>
                    <span class="pill" :class="statusTone(test.status)">{{ formatStatusLabel(test.status) }}</span>
                  </div>
                  <div class="course-history-item__stats">
                    <span>Верно: {{ formatPercent(test.correct_percentage) }}</span>
                    <span>Ошибки: {{ formatPercent(test.error_percentage) }}</span>
                  </div>
                  <div class="course-history-item__foot">
                    <span>{{ formatDate(test.started_at) }}</span>
                    <span>Разбор появится после отправки</span>
                  </div>
                </article>
              </template>
            </div>

            <PaginationControls
              v-if="detail.meta.total > detail.meta.limit"
              class="course-history-pagination"
              :total="detail.meta.total"
              :limit="detail.meta.limit"
              :offset="detail.meta.offset"
              :loading="loading"
              @prev="prevHistoryPage"
              @next="nextHistoryPage"
            />
          </div>
        </article>

        <article class="card card--muted">
          <div class="card__body">
            <h2 class="course-section-title">Темы</h2>
            <TopicPopoverList :topics="groupedTopics" />
          </div>
        </article>

        <article class="card">
          <div class="card__body">
            <h2 class="course-section-title">Описание</h2>
            <p class="course-copy">{{ detail.course.comment || 'Описание курса пока не добавлено.' }}</p>
          </div>
        </article>

        <article class="card card--muted">
          <div class="card__body">
            <h2 class="course-section-title">Указание для генерации</h2>
            <p class="course-copy">{{ detail.course.prompt || 'Дополнительное указание для генерации не задано.' }}</p>
          </div>
        </article>
      </section>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { api, ApiError } from '@/api/client'
import type { CourseDetail, CourseProgressItem, PaginatedCourseDetail } from '@/api/types'
import TopicPopoverList from '@/components/course/TopicPopoverList.vue'
import PaginationControls from '@/components/ui/PaginationControls.vue'
import { useAuthStore } from '@/stores/auth'
import { groupProgressTopics } from '@/utils/courseTopics'
import { formatDate, formatPercent, formatStatusLabel, statusTone } from '@/utils/format'
import { saveActiveTest } from '@/utils/testCache'

const props = defineProps<{ courseId: string }>()
const auth = useAuthStore()
const router = useRouter()

const detail = ref<PaginatedCourseDetail | null>(null)
const progress = ref<CourseProgressItem[]>([])
const enrolled = ref(false)
const loading = ref(false)
const generating = ref(false)
const deleting = ref(false)
const visibilityUpdating = ref(false)
const adminActionRunning = ref(false)
const error = ref('')
const success = ref('')
const historyLimit = 10
const historyOffset = ref(0)

const courseId = computed(() => Number(props.courseId))
const isAdmin = computed(() => auth.currentUser?.role === 'admin')
const isCreator = computed(() => detail.value?.course.creator_id === auth.currentUser?.id)
const canUseLearningActions = computed(() => enrolled.value || isCreator.value)
const canRestrictPublicAccess = computed(() => isAdmin.value && !isCreator.value && Boolean(detail.value?.course.is_public))
const canBlockCreator = computed(() => isAdmin.value && Boolean(detail.value?.course.creator_id) && !isCreator.value)
const groupedTopics = computed(() => groupProgressTopics(progress.value))
const activeInProgressTest = computed(() => {
  const latestTest = historyOffset.value === 0 ? detail.value?.tests[0] : null
  return latestTest && normalizedStatus(latestTest.status) === 'in_progress' ? latestTest : null
})
const generateTestDisabled = computed(() => generating.value || Boolean(activeInProgressTest.value))
const generateTestButtonLabel = computed(() => {
  if (generating.value) {
    return 'Генерируем...'
  }
  if (activeInProgressTest.value) {
    return 'Завершите текущий тест'
  }
  return 'Создать тест'
})
const visibilityActionLabel = computed(() => {
  if (!detail.value?.course) {
    return 'Изменить видимость'
  }
  return detail.value.course.is_public ? 'Сделать приватным' : 'Опубликовать'
})
const deleteActionLabel = computed(() => {
  return isCreator.value ? 'Удалить курс' : 'Убрать из моих курсов'
})

function normalizedStatus(status: string) {
  return status.toLowerCase()
}

function testActionLink(testId: number, status: string) {
  const normalized = normalizedStatus(status)
  if (normalized === 'finished') {
    return { name: 'course-test-review', params: { courseId: courseId.value, testId } }
  }
  if (normalized === 'in_progress') {
    return { name: 'course-test', params: { courseId: courseId.value, testId } }
  }
  return null
}

function testActionLabel(status: string) {
  return normalizedStatus(status) === 'in_progress' ? 'Продолжить тест' : 'Открыть разбор'
}

async function loadDetail() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    detail.value = await api.getCourseDetail(
      courseId.value,
      historyLimit,
      historyOffset.value,
    )
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось загрузить курс.'
  } finally {
    loading.value = false
  }
}

async function loadProgress() {
  try {
    const response = await api.getCourseProgress(courseId.value)
    progress.value = response.items
  } catch {
    progress.value = []
  }
}

async function loadMembership() {
  try {
    const membership = await api.getCourseMembership(courseId.value)
    enrolled.value = membership.enrolled
  } catch {
    enrolled.value = false
  }
}

async function reloadAll() {
  await Promise.all([loadDetail(), loadProgress(), loadMembership()])
}

function nextHistoryPage() {
  historyOffset.value += historyLimit
  void loadDetail()
}

function prevHistoryPage() {
  historyOffset.value = Math.max(0, historyOffset.value - historyLimit)
  void loadDetail()
}

async function generateTest() {
  if (generateTestDisabled.value) {
    return
  }

  generating.value = true
  error.value = ''
  try {
    const test = await api.createTest(courseId.value)
    saveActiveTest(test)
    await router.push({ name: 'course-test', params: { courseId: courseId.value, testId: test.id } })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось создать тест.'
  } finally {
    generating.value = false
  }
}

async function toggleVisibility() {
  if (!detail.value?.course) {
    return
  }

  visibilityUpdating.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await api.updateCourseVisibility(courseId.value, {
      is_public: !detail.value.course.is_public,
    })
    detail.value.course = response as CourseDetail
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось изменить видимость курса.'
  } finally {
    visibilityUpdating.value = false
  }
}

async function restrictPublicAccess() {
  if (!detail.value?.course) {
    return
  }

  adminActionRunning.value = true
  error.value = ''
  success.value = ''
  try {
    const response = await api.adminRestrictCoursePublicAccess(courseId.value)
    detail.value.course = response as CourseDetail
    success.value = 'Курс снят с общего доступа.'
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось снять курс с общего доступа.'
  } finally {
    adminActionRunning.value = false
  }
}

async function blockCreator() {
  const creatorId = detail.value?.course.creator_id
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

async function deleteCourse() {
  if (!detail.value?.course) {
    return
  }

  const confirmed = window.confirm(
    isCreator.value
      ? 'Удалить курс из вашей подборки? Если других записей нет, курс удалится полностью.'
      : 'Убрать этот курс из вашей подборки и удалить ваш прогресс по нему?',
  )
  if (!confirmed) {
    return
  }

  deleting.value = true
  error.value = ''
  try {
    await api.deleteCourse(courseId.value)
    await router.replace({
      name: 'courses',
      query: { refresh: String(Date.now()) },
    })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось удалить курс.'
  } finally {
    deleting.value = false
  }
}

watch(
  courseId,
  () => {
    historyOffset.value = 0
    void reloadAll()
  },
  { immediate: true },
)
</script>

<style scoped>
.course-scoreboard {
  min-width: 180px;
  display: grid;
  gap: 8px;
  justify-items: end;
  text-align: right;
}

.course-scoreboard strong {
  font-size: 58px;
  line-height: 0.95;
}

.course-scoreboard span:last-child {
  color: rgba(255, 255, 255, 0.72);
}

.course-detail-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 18px;
}

.course-detail-grid__history {
  grid-row: span 2;
}

.course-section-title {
  margin: 0 0 18px;
  font-size: 24px;
}

.course-detail-empty {
  margin-top: 8px;
}

.course-history-list {
  display: grid;
  gap: 12px;
}

.course-history-item {
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.72);
  transition:
    transform 180ms ease,
    background 180ms ease,
    border-color 180ms ease;
}

.course-history-item:hover {
  transform: translateY(-2px);
  background: white;
}

.course-history-item--disabled {
  opacity: 0.88;
}

.course-history-item__head,
.course-history-item__stats,
.course-history-item__foot {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.course-history-item__head h3 {
  margin: 0;
  font-size: 19px;
}

.course-history-item__head p,
.course-history-item__stats,
.course-history-item__foot {
  color: var(--muted);
}

.course-history-item__head p {
  margin: 5px 0 0;
}

.course-history-item__stats {
  margin-top: 14px;
}

.course-history-item__foot {
  margin-top: 18px;
  font-size: 13px;
}

.course-copy {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}

.course-history-pagination {
  margin-top: 18px;
}

@media (max-width: 1100px) {
  .course-detail-grid {
    grid-template-columns: 1fr;
  }

  .course-detail-grid__history {
    grid-row: auto;
  }
}

@media (max-width: 720px) {
  .course-scoreboard {
    justify-items: start;
    text-align: left;
  }
}
</style>
