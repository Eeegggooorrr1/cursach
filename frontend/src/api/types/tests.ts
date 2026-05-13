export interface TestOptionRead {
  id: number
  text: string
}

export interface TestQuestionRead {
  id: number
  subtopic_id: number
  prompt: string
  is_multiple_choice: boolean
  options: TestOptionRead[]
}

export interface TestRead {
  id: number
  course_id: number
  user_id: number
  position: number
  title: string
  questions: TestQuestionRead[]
}

export interface SubmitAnswer {
  question_id: number
  selected_option_ids: number[]
}

export interface TestSubmitPayload {
  answers: SubmitAnswer[]
}

export interface TestSubmitResponse {
  test_progress_id: number
  test_id: number
  status: string
  correct_percentage: number
}

export interface ReviewOption {
  id: number
  text: string
  is_correct: boolean
}

export interface ReviewQuestion {
  id: number
  subtopic_id: number
  prompt: string
  is_multiple_choice: boolean
  options: ReviewOption[]
}

export interface ReviewTest {
  id: number
  course_id: number
  position: number
  title: string
  questions: ReviewQuestion[]
}

export interface ReviewAttempt {
  question_id: number
  selected_option_ids: number[]
  is_correct: boolean
}

export interface TestReviewResponse {
  test: ReviewTest
  attempts: ReviewAttempt[]
}
