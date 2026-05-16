import { beforeEach, describe, expect, it } from 'vitest'
import type { TestRead } from '@/api/types'
import { clearActiveTest, readActiveTest, saveActiveTest } from './testCache'

const testPayload = {
  id: 7,
  course_id: 3,
  user_id: 5,
  position: 1,
  title: 'Test',
  questions: [],
} satisfies TestRead

describe('testCache', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('stores active tests by course and test identifiers', () => {
    saveActiveTest(testPayload)

    expect(readActiveTest(3, 7)).toEqual(testPayload)
    expect(readActiveTest(3, 8)).toBeNull()
    expect(readActiveTest(4, 7)).toBeNull()
  })

  it('clears active test cache entry', () => {
    saveActiveTest(testPayload)
    clearActiveTest(3, 7)

    expect(readActiveTest(3, 7)).toBeNull()
  })

  it('returns null for corrupted cache values', () => {
    sessionStorage.setItem('course-adapt-active-test:3:7', '{bad-json')

    expect(readActiveTest(3, 7)).toBeNull()
  })
})
