import request from './request'
import type { User, LoginRequest, Token } from '@/types'

export const authApi = {
  login(data: LoginRequest) {
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)
    return request.post<Token>('/auth/login', params)
  },

  register(data: { username: string; email: string; password: string; full_name?: string }) {
    return request.post<User>('/auth/register', data)
  },

  getMe() {
    return request.get<User>('/auth/me')
  },

  logout() {
    return request.post('/auth/logout')
  },

  changePassword(oldPassword: string | undefined, newPassword: string) {
    return request.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  }
}
