import { adminApi } from './admin'
import { authApi } from './auth'
import { courseApi } from './courses'
import { profileApi } from './profile'
import { testApi } from './tests'

export { ApiError } from './http'

export const api = {
  ...authApi,
  ...profileApi,
  ...courseApi,
  ...testApi,
  ...adminApi,
}
