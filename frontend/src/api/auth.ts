import request from './request'
import type { User, LoginRequest, Token } from '@/types'

export const authApi = {
  login(data: LoginRequest) {
    const formData = new FormData()
    formData.append('username', data.username)
    formData.append('password', data.password)
    return request.post<Token>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  
  register(data: { username: string; email: string; password: string; full_name?: string }) {
    return request.post<User>('/auth/register', data)
  },
  
  getMe() {
    return request.get<User>('/auth/me')
  },
  
  logout() {
    return request.post('/auth/logout')
  }
}
