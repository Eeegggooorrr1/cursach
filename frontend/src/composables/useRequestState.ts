import { ref } from 'vue'

export function useRequestState() {
  const loading = ref(false)
  const error = ref('')
  const success = ref('')

  function reset() {
    error.value = ''
    success.value = ''
  }

  async function run<T>(task: () => Promise<T>, fallbackMessage: string): Promise<T | null> {
    loading.value = true
    reset()

    try {
      return await task()
    } catch (e) {
      error.value = e instanceof Error && e.message ? e.message : fallbackMessage
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    success,
    reset,
    run,
  }
}
