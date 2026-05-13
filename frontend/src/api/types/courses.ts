import type { DifficultyLevel, PaginationMeta } from './common'

export interface CourseListItem {
  id: number
  creator_id: number
  title: string
  comment: string | null
  is_public: boolean
  is_public_allowed: boolean
  created_at: string
}

export interface CourseDetail {
  id: number
  creator_id: number
  title: string
  comment: string | null
  prompt: string | null
  is_public: boolean
  is_public_allowed: boolean
  created_at: string
}

export interface SubtopicRead {
  id: number
  name: string
}

export interface TopicRead {
  id: number
  name: string
  subtopics: SubtopicRead[]
}

export interface CourseRead {
  id: number
  creator_id: number
  title: string
  comment: string | null
  prompt: string | null
  is_public: boolean
  is_public_allowed: boolean
  created_at: string
  topics: TopicRead[]
}

export interface PublicCourseDetail {
  id: number
  creator_id: number
  title: string
  comment: string | null
  is_public: boolean
  is_public_allowed: boolean
  created_at: string
  topics: TopicRead[]
}

export interface CourseCreatePayload {
  title: string
  comment?: string | null
  prompt?: string | null
  topics: string[]
  initial_difficulty: DifficultyLevel
  is_public: boolean
}

export interface CourseEnrollPayload {
  initial_difficulty: DifficultyLevel
}

export interface CourseEnrollmentResponse {
  course_id: number
  user_id: number
  enrolled: boolean
}

export interface CourseMembership {
  course_id: number
  user_id: number
  enrolled: boolean
  owned: boolean
}

export interface CourseVisibilityUpdatePayload {
  is_public: boolean
}

export interface CourseProgressItem {
  topic_id: number
  topic_name: string
  subtopic_id: number
  subtopic_name: string
  mastery_score: number
  current_difficulty: number
  current_streak: number
}

export interface CourseProgressResponse {
  items: CourseProgressItem[]
}

export interface CourseHistoryTestItem {
  id: number
  position: number
  title: string
  status: string
  correct_percentage: number
  error_percentage: number
  started_at: string
  finished_at: string | null
}

export interface PaginatedCourseList {
  items: CourseListItem[]
  meta: PaginationMeta
}

export interface DashboardLastTest {
  course_id: number
  test_id: number
  course_title: string
  test_title: string
  questions_count: number
  incorrect_answers_count: number
  correct_percentage: number
  started_at: string
  finished_at: string | null
}

export interface CourseDashboardSummary {
  active_courses: number
  tests_last_week: number
  shared_courses: number
  public_courses: number
  last_test: DashboardLastTest | null
}

export interface PaginatedCourseDetail {
  course: CourseDetail
  tests: CourseHistoryTestItem[]
  meta: PaginationMeta
}
