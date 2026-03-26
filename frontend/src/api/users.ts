import request from './request'
import type { User } from '@/types'

export interface UserForm {
  username: string
  email: string
  full_name?: string
  password: string
  is_superuser?: boolean
}

export const usersApi = {
  list(params?: { page?: number; page_size?: number; keyword?: string }) {
    return request.get<{ total: number; items: User[] }>('/users', { params })
  },
  
  get(id: number) {
    return request.get<User>(`/users/${id}`)
  },
  
  create(data: UserForm) {
    return request.post<User>('/users', data)
  },
  
  update(id: number, data: Partial<UserForm>) {
    return request.put<User>(`/users/${id}`, data)
  },
  
  delete(id: number) {
    return request.delete(`/users/${id}`)
  },
  
  changePassword(userId: number, oldPassword: string, newPassword: string) {
    return request.put(`/users/${userId}/password`, null, {
      params: { old_password: oldPassword, new_password: newPassword }
    })
  }
}
