import { request } from './http'
import type { AdminUser, CourseDetail, PaginatedAdminCourseList, PaginatedAdminUserList } from './types'

export const adminApi = {
  getBlockedUsers(limit = 20, offset = 0) {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    return request<PaginatedAdminUserList>(`/admin/blocked-users?${params.toString()}`)
  },
  getRestrictedCourses(limit = 20, offset = 0) {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    return request<PaginatedAdminCourseList>(`/admin/restricted-courses?${params.toString()}`)
  },
  adminBlockUser(userId: number) {
    return request<AdminUser>(`/admin/users/${userId}/block`, {
      method: 'PATCH',
    })
  },
  adminUnblockUser(userId: number) {
    return request<AdminUser>(`/admin/users/${userId}/unblock`, {
      method: 'PATCH',
    })
  },
  adminRestrictCoursePublicAccess(courseId: number) {
    return request<CourseDetail>(`/admin/courses/${courseId}/restrict-public`, {
      method: 'PATCH',
    })
  },
  adminRestoreCoursePublicAccess(courseId: number) {
    return request<CourseDetail>(`/admin/courses/${courseId}/restore-public`, {
      method: 'PATCH',
    })
  },
}
