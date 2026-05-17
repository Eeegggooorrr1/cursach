<template>
  <section class="page-stack courses-page">
    <header class="workspace-head glass courses-head">
      <div>
        <p class="eyebrow">Мои курсы</p>
        <h1>{{ headerMoodline }}</h1>
      </div>
      <div class="head-actions">
        <RouterLink class="icon-btn" :to="{ name: 'catalog' }" aria-label="Открыть каталог" title="Каталог">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M11 19a8 8 0 1 1 5.3-14M21 21l-4.35-4.35"
              fill="none"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.8"
            />
          </svg>
        </RouterLink>
        <RouterLink class="button button--secondary" to="/courses/new">Создать курс</RouterLink>
      </div>
    </header>

    <section class="metrics-grid">
      <article class="metric-card glass reveal">
        <span>Активных курсов</span>
        <strong>{{ summary?.active_courses ?? meta.total }}</strong>
        <div class="metric-card__line metric-card__line--green"></div>
      </article>
      <article class="metric-card glass reveal delay-1">
        <span>Тестов за неделю</span>
        <strong>{{ summary?.tests_last_week ?? '--' }}</strong>
        <div class="metric-card__line metric-card__line--blue"></div>
      </article>
      <article class="metric-card glass reveal delay-2">
        <span>Добавленных курсов</span>
        <strong>{{ summary?.shared_courses ?? sharedCoursesOnPage }}</strong>
        <div class="metric-card__line metric-card__line--amber"></div>
      </article>
      <article class="metric-card glass reveal delay-3">
        <span>Публичных курсов</span>
        <strong>{{ summary?.public_courses ?? publicCoursesOnPage }}</strong>
        <div class="metric-card__line metric-card__line--red"></div>
      </article>
    </section>

    <div v-if="error" class="notice notice--error">{{ error }}</div>

    <section class="dashboard-layout">
      <div class="main-column">
        <article class="focus-panel reveal">
          <div class="focus-panel__media">
            <div class="test-score-orbit" :style="lastTestScoreStyle">
              <strong>{{ lastTestScore }}</strong>
              <span>верно</span>
            </div>
          </div>
          <div class="focus-panel__content">
            <span class="pill pill--dark">Последний тест</span>
            <h2>{{ lastTestTitle }}</h2>
            <div class="last-test-grid" v-if="summary?.last_test">
              <span><strong>{{ summary.last_test.questions_count }}</strong> вопросов</span>
              <span><strong>{{ summary.last_test.incorrect_answers_count }}</strong> ошибок</span>
            </div>
            <div class="focus-panel__actions">
              <RouterLink
                v-if="summary?.last_test"
                class="button button--ghost"
                :to="{
                  name: 'course-test-review',
                  params: {
                    courseId: summary.last_test.course_id,
                    testId: summary.last_test.test_id,
                  },
                }"
              >
                Открыть разбор
              </RouterLink>
            </div>
          </div>
        </article>

        <div class="section-row">
          <h2>Курсы</h2>
          <span class="pill">Всего: {{ meta.total }}</span>
        </div>

        <div v-if="loading" class="notice">Загружаем курсы...</div>
        <div v-else-if="items.length === 0" class="empty-state">
          Пока здесь пусто. Можно создать свой курс или взять публичный из каталога.
        </div>

        <section v-else class="course-mosaic">
          <RouterLink
            v-for="(course, index) in items"
            :key="course.id"
            class="course-block reveal interactive-card"
            :class="[`course-block--tone-${(index % 4) + 1}`]"
            :to="`/courses/${course.id}`"
          >
            <span class="course-block__status">
              {{ course.creator_id === auth.currentUser?.id ? (course.is_public ? 'ваш публичный' : 'ваш курс') : 'добавлен' }}
            </span>
            <div class="course-block__body">
              <h3>{{ course.title }}</h3>
              <p>{{ course.comment || 'Описание пока не добавлено.' }}</p>
            </div>
            <div class="course-block__meta">
              <span>{{ course.is_public ? 'Публичный доступ' : 'Приватный курс' }}</span>
              <span>{{ formatDate(course.created_at) }}</span>
            </div>
          </RouterLink>
        </section>
      </div>

      <aside class="side-column">
        <RouterLink class="catalog-card reveal delay-1 interactive-card" :to="{ name: 'catalog' }">
          <span class="pill">Каталог</span>
          <h2>Найти готовый курс</h2>
          <label class="search-box">
            <span>⌕</span>
            <input value="" placeholder="Machine learning" readonly />
          </label>
        </RouterLink>
      </aside>
    </section>

    <PaginationControls
      v-if="meta.total > meta.limit"
      :total="meta.total"
      :limit="meta.limit"
      :offset="meta.offset"
      :loading="loading"
      @prev="prevPage"
      @next="nextPage"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { api, ApiError } from '@/api/client'
import type { CourseDashboardSummary, CourseListItem, PaginationMeta } from '@/api/types'
import PaginationControls from '@/components/ui/PaginationControls.vue'
import { useAuthStore } from '@/stores/auth'
import { formatDate, formatPercent } from '@/utils/format'

const auth = useAuthStore()
const route = useRoute()
const moodlines = [
  'Сегодня можно хорошо продвинуться в одной теме',
  'Вернитесь к курсу, который давно ждет вас',
  'Пора открыть что-то новое или дожать начатое',
  'Небольшой тест сейчас даст хороший темп',
]
const loading = ref(false)
const error = ref('')
const items = ref<CourseListItem[]>([])
const summary = ref<CourseDashboardSummary | null>(null)
const meta = reactive<PaginationMeta>({
  total: 0,
  limit: 8,
  offset: 0,
})
const headerMoodline = moodlines[Math.floor(Math.random() * moodlines.length)]

const sharedCoursesOnPage = computed(() => {
  return items.value.filter((course) => course.creator_id !== auth.currentUser?.id).length
})
const publicCoursesOnPage = computed(() => items.value.filter((course) => course.is_public).length)
const lastTestTitle = computed(() => {
  if (!summary.value?.last_test) {
    return 'История последнего завершенного теста появится здесь'
  }
  return `${summary.value.last_test.course_title}: ${summary.value.last_test.test_title}`
})
const lastTestScore = computed(() => {
  if (!summary.value?.last_test) {
    return '--'
  }
  return formatPercent(summary.value.last_test.correct_percentage)
})
const lastTestScoreStyle = computed(() => {
  const value = summary.value?.last_test?.correct_percentage
  const percent = Number.isFinite(Number(value))
    ? Math.max(0, Math.min(100, Number(value)))
    : 0

  return {
    '--last-test-score': `${percent}%`,
  }
})

async function loadCourses() {
  loading.value = true
  error.value = ''
  try {
    const [coursesResponse, summaryResponse] = await Promise.all([
      api.getMyCourses(meta.limit, meta.offset),
      api.getCourseDashboardSummary(),
    ])
    items.value = coursesResponse.items
    meta.total = coursesResponse.meta.total
    meta.limit = coursesResponse.meta.limit
    meta.offset = coursesResponse.meta.offset
    summary.value = summaryResponse
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось загрузить ваши курсы.'
  } finally {
    loading.value = false
  }
}

function nextPage() {
  meta.offset += meta.limit
  loadCourses()
}

function prevPage() {
  meta.offset = Math.max(0, meta.offset - meta.limit)
  loadCourses()
}

onMounted(loadCourses)

watch(
  () => route.query.refresh,
  () => {
    loadCourses()
  },
)
</script>

<style scoped></style>
