import type { TestRead } from '@/api/types'

const ACTIVE_TEST_PREFIX = 'course-adapt-active-test'

export function saveActiveTest(test: TestRead) {
  sessionStorage.setItem(`${ACTIVE_TEST_PREFIX}:${test.course_id}:${test.id}`, JSON.stringify(test))
}

export function readActiveTest(courseId: number, testId: number): TestRead | null {
  try {
    const raw = sessionStorage.getItem(`${ACTIVE_TEST_PREFIX}:${courseId}:${testId}`)
    if (!raw) {
      return null
    }
    return JSON.parse(raw) as TestRead
  } catch {
    return null
  }
}

export function clearActiveTest(courseId: number, testId: number) {
  sessionStorage.removeItem(`${ACTIVE_TEST_PREFIX}:${courseId}:${testId}`)
}
