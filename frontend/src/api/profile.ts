import { request } from './http'
import type { UserProfile, UserProfileUpdatePayload } from './types'

export const profileApi = {
  getProfile() {
    return request<UserProfile>('/profile/')
  },
  updateProfile(payload: UserProfileUpdatePayload) {
    return request<UserProfile>('/profile/', {
      method: 'PATCH',
      body: payload,
    })
  },
}
