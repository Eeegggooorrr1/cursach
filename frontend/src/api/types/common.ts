export type Nullable<T> = T | null
export type DifficultyLevel = 0 | 1 | 2

export interface ApiErrorDetail {
  loc?: Array<string | number>
  msg?: string
  type?: string
}

export interface ApiErrorEnvelope {
  code?: string
  message?: string
}

export interface ApiErrorPayload {
  detail?: ApiErrorDetail[] | string
  message?: string
  error?: ApiErrorEnvelope
}

export interface ApiMessageResponse {
  msg: string
}

export interface PaginationMeta {
  total: number
  limit: number
  offset: number
}
