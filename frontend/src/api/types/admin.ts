import type { PaginationMeta } from './common'

export interface AdminUser {
  id: number
  email: string
  username: string
  profile_description: string | null
  is_blocked: boolean
  role: string
}

export interface AdminCourse {
  id: number
  creator_id: number
  creator_email: string
  creator_username: string
  title: string
  comment: string | null
  is_public: boolean
  is_public_allowed: boolean
  created_at: string
}

export interface PaginatedAdminUserList {
  items: AdminUser[]
  meta: PaginationMeta
}

export interface PaginatedAdminCourseList {
  items: AdminCourse[]
  meta: PaginationMeta
}
