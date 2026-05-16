import type { SessionUser } from '@/api/types'

const LOGOUT_LOCK_KEY = 'course-adapt-logout-lock'
const ACCESS_COOKIE_NAME = 'user_access_token'

interface JwtClaims {
  sub?: string
  username?: string
  role?: string
  is_blocked?: boolean
  exp?: number
}

function decodeBase64Url(value: string) {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/')
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
  return atob(padded)
}

function readCookie(name: string): string | null {
  if (typeof document === 'undefined') {
    return null
  }

  const pair = document.cookie
    .split('; ')
    .find((entry) => entry.startsWith(`${encodeURIComponent(name)}=`) || entry.startsWith(`${name}=`))

  if (!pair) {
    return null
  }

  const value = pair.includes('=') ? pair.split('=').slice(1).join('=') : ''
  return value ? decodeURIComponent(value) : null
}

function clearCookie(name: string) {
  if (typeof document === 'undefined') {
    return
  }

  document.cookie = `${encodeURIComponent(name)}=; Max-Age=0; path=/; SameSite=Lax`
}

function parseJwtClaims(token: string | null): JwtClaims | null {
  if (!token) {
    return null
  }

  const parts = token.split('.')
  if (parts.length < 2) {
    return null
  }

  try {
    return JSON.parse(decodeBase64Url(parts[1])) as JwtClaims
  } catch {
    return null
  }
}

function isExpired(exp: number | undefined) {
  if (!exp) {
    return false
  }
  return exp * 1000 <= Date.now()
}

export function setLogoutLock(value: boolean) {
  if (value) {
    localStorage.setItem(LOGOUT_LOCK_KEY, '1')
  } else {
    localStorage.removeItem(LOGOUT_LOCK_KEY)
  }
}

export function clearLogoutLock() {
  localStorage.removeItem(LOGOUT_LOCK_KEY)
}

export function isLogoutLocked() {
  return localStorage.getItem(LOGOUT_LOCK_KEY) === '1'
}

export function clearAccessTokenCookie() {
  clearCookie(ACCESS_COOKIE_NAME)
}

export function readAccessToken() {
  return readCookie(ACCESS_COOKIE_NAME)
}

export function readSessionUser(): SessionUser | null {
  const claims = parseJwtClaims(readAccessToken())
  if (!claims?.sub || isExpired(claims.exp)) {
    return null
  }

  const id = Number(claims.sub)
  if (!Number.isFinite(id)) {
    return null
  }

  return {
    id,
    username: claims.username || 'Пользователь',
    role: claims.role || null,
    is_blocked: Boolean(claims.is_blocked),
  }
}
