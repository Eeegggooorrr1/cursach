<template>
  <section class="page-stack catalog-page">
    <section class="search-screen-head">
      <span class="pill pill--dark">Каталог</span>
      <h1>Поиск публичных курсов</h1>
      <form class="big-search" @submit.prevent="applySearch">
        <span>⌕</span>
        <input
          v-model.trim="filters.query"
          type="search"
          placeholder="Название или описание курса"
        />
        <button type="submit" :disabled="loading">Найти</button>
      </form>
      <div class="catalog-toolbar">
        <select v-model="filters.sort" class="select catalog-toolbar__select" @change="applySearch">
          <option value="created_desc">Сначала новые</option>
          <option value="created_asc">Сначала старые</option>
        </select>
        <button class="button button--ghost" type="button" :disabled="loading" @click="resetSearch">Сбросить</button>
      </div>
    </section>

    <div v-if="error" class="notice notice--error">{{ error }}</div>
    <div v-else-if="loading" class="notice">Загружаем каталог...</div>
    <div v-else-if="items.length === 0" class="empty-state">
      В каталоге пока нет подходящих курсов.
    </div>

    <section v-else class="search-results-grid">
      <RouterLink
        v-for="course in items"
        :key="course.id"
        class="search-result"
        :to="{ name: 'catalog-course', params: { courseId: course.id } }"
      >
        <span class="pill">
          {{ course.creator_id === auth.currentUser?.id ? 'ваш публичный курс' : 'публичный курс' }}
        </span>
        <div class="search-result__body">
          <h2>{{ course.title }}</h2>
          <p>{{ course.comment || 'Описание пока не добавлено.' }}</p>
        </div>
        <div class="search-result__foot">
          <span>{{ formatDate(course.created_at) }}</span>
          <span>Открыть карточку</span>
        </div>
      </RouterLink>
    </section>

    <PaginationControls
      v-if="meta.total > meta.limit"
      :total="meta.total"
      :limit="meta.limit"
      :offset="meta.offset"
      :loading="loading"
      label="Найдено"
      summary="total"
      @prev="prevPage"
      @next="nextPage"
    />
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { api } from '@/api/client'
import type { CourseListItem, PaginationMeta } from '@/api/types'
import PaginationControls from '@/components/ui/PaginationControls.vue'
import { useRequestState } from '@/composables/useRequestState'
import { useAuthStore } from '@/stores/auth'
import { formatDate } from '@/utils/format'

const auth = useAuthStore()
const { loading, error, run } = useRequestState()
const items = ref<CourseListItem[]>([])
const filters = reactive({
  query: '',
  sort: 'created_desc' as 'created_desc' | 'created_asc',
})
const meta = reactive<PaginationMeta>({
  total: 0,
  limit: 8,
  offset: 0,
})

async function loadCourses() {
  await run(async () => {
    const response = await api.getPublicCourses(
      meta.limit,
      meta.offset,
      filters.query,
      filters.sort,
    )
    items.value = response.items
    meta.total = response.meta.total
    meta.limit = response.meta.limit
    meta.offset = response.meta.offset
  }, 'Не удалось загрузить каталог.')
}

function nextPage() {
  meta.offset += meta.limit
  loadCourses()
}

function prevPage() {
  meta.offset = Math.max(0, meta.offset - meta.limit)
  loadCourses()
}

function applySearch() {
  meta.offset = 0
  loadCourses()
}

function resetSearch() {
  filters.query = ''
  filters.sort = 'created_desc'
  applySearch()
}

onMounted(loadCourses)
</script>

<style scoped>
.catalog-toolbar__select {
  min-width: 220px;
  padding-right: 46px;
  border-radius: 18px;
  color: var(--text);
  background-color: rgba(255, 255, 255, 0.92);
  background-image:
    linear-gradient(180deg, rgba(255, 255, 255, 0.18), rgba(17, 24, 39, 0.03)),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%23111827' stroke-width='1.9' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat, no-repeat;
  background-position: 0 0, calc(100% - 16px) 50%;
  background-size: auto, 14px;
  box-shadow: 0 16px 30px rgba(17, 24, 39, 0.08);
  appearance: none;
}

.catalog-toolbar__select:hover {
  border-color: rgba(17, 97, 73, 0.2);
  background-color: white;
}

.catalog-toolbar__select option {
  color: var(--text);
  background: white;
}
</style>
