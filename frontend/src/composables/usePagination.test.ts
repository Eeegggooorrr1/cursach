import { ref } from 'vue'
import { describe, expect, it } from 'vitest'
import { usePagination } from './usePagination'

describe('usePagination', () => {
  it('derives current page and boundary flags from offset', () => {
    const total = ref(25)
    const limit = ref(10)
    const offset = ref(10)

    const pagination = usePagination({ total, limit, offset })

    expect(pagination.page.value).toBe(1)
    expect(pagination.isFirstPage.value).toBe(false)
    expect(pagination.isLastPage.value).toBe(false)
  })

  it('moves between pages without crossing boundaries', () => {
    const total = ref(20)
    const limit = ref(10)
    const offset = ref(0)

    const pagination = usePagination({ total, limit, offset })

    pagination.prevPage()
    expect(offset.value).toBe(0)

    pagination.nextPage()
    expect(offset.value).toBe(10)
    expect(pagination.isLastPage.value).toBe(true)

    pagination.nextPage()
    expect(offset.value).toBe(10)

    pagination.resetPage()
    expect(offset.value).toBe(0)
  })
})
