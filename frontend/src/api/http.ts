import type { ApiErrorPayload } from './types'
import { isLogoutLocked, readAccessToken } from '@/utils/authSession'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export type RequestOptions = Omit<RequestInit, 'body'> & {
  body?: unknown
  auth?: boolean
}

export class ApiError extends Error {
  status: number
  payload: ApiErrorPayload | null

  constructor(message: string, status: number, payload: ApiErrorPayload | null = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

let refreshPromise: Promise<boolean> | null = null

function isJsonResponse(response: Response) {
  const contentType = response.headers.get('content-type') || ''
  return contentType.includes('application/json')
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204 || !isJsonResponse(response)) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

function extractMessage(payload: ApiErrorPayload | null, fallback: string) {
  if (!payload) {
    return fallback
  }

  if (payload.error?.message) {
    return payload.error.message
  }

  if (typeof payload.detail === 'string' && payload.detail.trim()) {
    return payload.detail
  }

  if (Array.isArray(payload.detail) && payload.detail.length > 0) {
    return payload.detail[0]?.msg || fallback
  }

  if (payload.message) {
    return payload.message
  }

  return fallback
}

async function readError(response: Response): Promise<ApiErrorPayload | null> {
  try {
    if (!isJsonResponse(response)) {
      return null
    }
    return (await response.json()) as ApiErrorPayload
  } catch {
    return null
  }
}

async function refreshSession(): Promise<boolean> {
  if (isLogoutLocked()) {
    return false
  }

  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const response = await fetch(`${API_BASE}/auth/refresh`, {
          method: 'POST',
          credentials: 'include',
        })

        return response.ok
      } catch {
        return false
      } finally {
        refreshPromise = null
      }
    })()
  }

  return refreshPromise
}

export async function request<T>(path: string, options: RequestOptions = {}, retry = true): Promise<T> {
  const headers = new Headers(options.headers)

  if (!(options.body instanceof FormData) && options.body !== undefined) {
    headers.set('content-type', 'application/json')
  }

  if (options.auth !== false) {
    const token = readAccessToken()
    if (token) {
      headers.set('authorization', token.startsWith('Bearer ') ? token : `Bearer ${token}`)
    }
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body: options.body instanceof FormData || options.body === undefined ? options.body : JSON.stringify(options.body),
    credentials: 'include',
    cache: 'no-store',
  })

  if (response.status === 401 && options.auth !== false && retry && !isLogoutLocked()) {
    const refreshed = await refreshSession()
    if (refreshed) {
      return request<T>(path, options, false)
    }
  }

  if (!response.ok) {
    const payload = await readError(response)
    throw new ApiError(extractMessage(payload, `Request failed with status ${response.status}`), response.status, payload)
  }

  return parseResponse<T>(response)
}
