export interface SessionUser {
  id: number
  username: string
  role: string | null
  is_blocked: boolean
}

export interface UserProfile {
  id: number
  email: string
  username: string
  profile_description: string | null
  is_blocked: boolean
  role: string
}

export interface UserProfileUpdatePayload {
  profile_description: string | null
}

export interface UserLoginPayload {
  email: string
  password: string
}

export interface UserRegisterPayload {
  email: string
  password: string
  username: string
  profile_description?: string | null
}
