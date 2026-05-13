import { request } from './http'
import type { TestRead, TestReviewResponse, TestSubmitPayload, TestSubmitResponse } from './types'

export const testApi = {
  createTest(courseId: number) {
    return request<TestRead>(`/courses/${courseId}/create-test`, {
      method: 'POST',
    })
  },
  getTest(courseId: number, testId: number) {
    return request<TestRead>(`/courses/${courseId}/tests/${testId}`)
  },
  submitTest(courseId: number, testId: number, payload: TestSubmitPayload) {
    return request<TestSubmitResponse>(`/courses/${courseId}/${testId}/submit`, {
      method: 'POST',
      body: payload,
    })
  },
  getTestReview(courseId: number, testId: number) {
    return request<TestReviewResponse>(`/courses/${courseId}/${testId}/review`)
  },
}
