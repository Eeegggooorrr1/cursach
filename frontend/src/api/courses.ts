import { request } from './http'
import type {
  CourseCreatePayload,
  CourseDashboardSummary,
  CourseDetail,
  CourseEnrollmentResponse,
  CourseEnrollPayload,
  CourseMembership,
  CourseProgressResponse,
  CourseRead,
  CourseVisibilityUpdatePayload,
  PaginatedCourseDetail,
  PaginatedCourseList,
  PublicCourseDetail,
} from './types'

export const courseApi = {
  getMyCourses(limit = 20, offset = 0) {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    return request<PaginatedCourseList>(`/courses/?${params.toString()}`)
  },
  getCourseDashboardSummary() {
    return request<CourseDashboardSummary>('/courses/summary')
  },
  getPublicCourses(limit = 20, offset = 0, query = '', sort: 'created_desc' | 'created_asc' = 'created_desc') {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    if (query.trim()) {
      params.set('q', query.trim())
    }
    params.set('sort', sort)
    return request<PaginatedCourseList>(`/courses/public?${params.toString()}`, { auth: false })
  },
  createCourse(payload: CourseCreatePayload) {
    return request<CourseRead>('/courses/', {
      method: 'POST',
      body: payload,
    })
  },
  getCourseDetail(courseId: number, limit = 20, offset = 0) {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    return request<PaginatedCourseDetail>(`/courses/${courseId}?${params.toString()}`)
  },
  getPublicCourseDetail(courseId: number) {
    return request<PublicCourseDetail>(`/courses/public/${courseId}`, { auth: false })
  },
  enrollPublicCourse(courseId: number, payload: CourseEnrollPayload) {
    return request<CourseEnrollmentResponse>(`/courses/${courseId}/enroll`, {
      method: 'POST',
      body: payload,
    })
  },
  getCourseMembership(courseId: number) {
    return request<CourseMembership>(`/courses/${courseId}/membership`)
  },
  updateCourseVisibility(courseId: number, payload: CourseVisibilityUpdatePayload) {
    return request<CourseDetail>(`/courses/${courseId}/visibility`, {
      method: 'PATCH',
      body: payload,
    })
  },
  deleteCourse(courseId: number) {
    return request<void>(`/courses/${courseId}`, {
      method: 'DELETE',
    })
  },
  getCourseProgress(courseId: number) {
    return request<CourseProgressResponse>(`/courses/${courseId}/progress`)
  },
}
