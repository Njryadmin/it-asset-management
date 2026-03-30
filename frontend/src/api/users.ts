import request from './request'
import type { User } from '@/types'

export interface UserCreateForm {
  username: string
  email: string
  full_name?: string
  password: string
  is_superuser?: boolean
}

export interface UserUpdateForm {
  email?: string
  full_name?: string
  password?: string
  is_superuser?: boolean
  is_active?: boolean
}

export const usersApi = {
  list(params?: { page?: number; page_size?: number; keyword?: string }) {
    return request.get<{ total: number; items: User[] }>('/users', { params })
  },
  
  get(id: number) {
    return request.get<User>(`/users/${id}`)
  },
  
  create(data: UserCreateForm) {
    return request.post<User>('/users', data)
  },
  
  update(id: number, data: Partial<UserUpdateForm>) {
    return request.put<User>(`/users/${id}`, data)
  },
  
  delete(id: number) {
    return request.delete(`/users/${id}`)
  },
  
  changePassword(userId: number, oldPassword: string | undefined, newPassword: string) {
    return request.put(`/users/${userId}/password`, {
      old_password: oldPassword,
      new_password: newPassword
    })
  },

  toggleStatus(id: number) {
    return request.post(`/users/${id}/toggle-status`)
  },

  resetPassword(id: number) {
    return request.post<{ temp_password: string; message: string }>(`/users/${id}/reset-password`)
  }
}
