<template>
  <div class="split">
    <span class="pill">{{ summaryText }}</span>
    <div class="actions">
      <button class="button button--secondary" type="button" :disabled="isFirstPage || loading" @click="$emit('prev')">
        Назад
      </button>
      <button class="button button--secondary" type="button" :disabled="isLastPage || loading" @click="$emit('next')">
        Вперед
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, toRef } from 'vue'
import { usePagination } from '@/composables/usePagination'

const props = withDefaults(
  defineProps<{
    total: number
    limit: number
    offset: number
    loading?: boolean
    label?: string
    summary?: 'page' | 'total'
  }>(),
  {
    loading: false,
    label: 'Страница',
    summary: 'page',
  },
)

defineEmits<{
  prev: []
  next: []
}>()

const { page, isFirstPage, isLastPage } = usePagination({
  total: toRef(props, 'total'),
  limit: toRef(props, 'limit'),
  offset: toRef(props, 'offset'),
})

const summaryText = computed(() => {
  if (props.summary === 'total') {
    return `${props.label}: ${props.total}`
  }
  return `${props.label} ${page.value + 1}`
})
</script>
