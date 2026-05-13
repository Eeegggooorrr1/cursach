import { request } from './http'
import type { ApiMessageResponse, UserLoginPayload, UserRegisterPayload } from './types'

export const authApi = {
  login(payload: UserLoginPayload) {
    return request<ApiMessageResponse>('/auth/login', {
      method: 'POST',
      auth: false,
      body: payload,
    })
  },
  register(payload: UserRegisterPayload) {
    return request<ApiMessageResponse>('/auth/register', {
      method: 'POST',
      auth: false,
      body: payload,
    })
  },
  refresh() {
    return request<ApiMessageResponse>('/auth/refresh', {
      method: 'POST',
      auth: false,
    })
  },
  logout() {
    return request<ApiMessageResponse>('/auth/logout', {
      method: 'POST',
    })
  },
}
