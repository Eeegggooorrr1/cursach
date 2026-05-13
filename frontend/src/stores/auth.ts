import { defineStore } from 'pinia'
import type { SessionUser, UserLoginPayload, UserRegisterPayload } from '@/api/types'
import { api } from '@/api/client'
import {
  clearAccessTokenCookie,
  clearLogoutLock,
  isLogoutLocked,
  readSessionUser,
  setLogoutLock,
} from '@/utils/authSession'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: readSessionUser() as SessionUser | null,
    ready: false,
    bootstrapPromise: null as Promise<void> | null,
  }),
  getters: {
    isAuthenticated(state): boolean {
      return Boolean(state.user)
    },
    currentUser(state): SessionUser | null {
      return state.user
    },
  },
  actions: {
    syncFromCookie() {
      clearLogoutLock()
      this.user = readSessionUser()
      this.ready = true
    },
    clear() {
      this.user = null
      clearAccessTokenCookie()
    },
    async bootstrap() {
      if (this.ready) {
        return
      }
      if (this.bootstrapPromise) {
        return this.bootstrapPromise
      }

      this.bootstrapPromise = (async () => {
        try {
          const currentUser = readSessionUser()
          if (currentUser) {
            this.user = currentUser
            return
          }

          if (isLogoutLocked()) {
            this.clear()
            return
          }

          await api.refresh()
          this.user = readSessionUser()
        } catch {
          this.clear()
        } finally {
          this.ready = true
          this.bootstrapPromise = null
        }
      })()

      return this.bootstrapPromise
    },
    async login(payload: UserLoginPayload) {
      await api.login(payload)
      this.syncFromCookie()
    },
    async register(payload: UserRegisterPayload) {
      await api.register(payload)
      this.syncFromCookie()
    },
    async logout() {
      try {
        await api.logout()
      } finally {
        setLogoutLock(true)
        this.clear()
        this.ready = true
      }
    },
  },
})
