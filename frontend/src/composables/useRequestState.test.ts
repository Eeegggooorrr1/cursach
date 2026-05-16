import { describe, expect, it } from 'vitest'
import { useRequestState } from './useRequestState'

describe('useRequestState', () => {
  it('stores successful task result and resets messages before run', async () => {
    const state = useRequestState()
    state.error.value = 'Previous error'
    state.success.value = 'Previous success'

    const result = await state.run(async () => 'ok', 'fallback')

    expect(result).toBe('ok')
    expect(state.loading.value).toBe(false)
    expect(state.error.value).toBe('')
    expect(state.success.value).toBe('')
  })

  it('stores error message and returns null when task fails', async () => {
    const state = useRequestState()

    const result = await state.run(async () => {
      throw new Error('Failed request')
    }, 'fallback')

    expect(result).toBeNull()
    expect(state.loading.value).toBe(false)
    expect(state.error.value).toBe('Failed request')
  })
})
