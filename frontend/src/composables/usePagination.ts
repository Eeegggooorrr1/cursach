import { computed, type Ref } from 'vue'

export type PaginationInput = {
  total: Ref<number>
  limit: Ref<number>
  offset: Ref<number>
}

export function usePagination({ total, limit, offset }: PaginationInput) {
  const page = computed(() => Math.floor(offset.value / limit.value))
  const isFirstPage = computed(() => page.value === 0)
  const isLastPage = computed(() => offset.value + limit.value >= total.value)

  function nextPage() {
    if (!isLastPage.value) {
      offset.value += limit.value
    }
  }

  function prevPage() {
    offset.value = Math.max(0, offset.value - limit.value)
  }

  function resetPage() {
    offset.value = 0
  }

  return {
    page,
    isFirstPage,
    isLastPage,
    nextPage,
    prevPage,
    resetPage,
  }
}
