import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApi } from '@/composables/useApi'

export const useAuthStore = defineStore('auth', () => {
  const { fetchApi } = useApi()

  const token = ref(localStorage.getItem('token'))
  const user = ref(JSON.parse(localStorage.getItem('user')))
  const isAuthenticated = computed(() => !!token.value)

  const login = async (username, password) => {
    
      const data = await fetchApi('/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      })
      
      token.value = data.access_token
      user.value = { username: data.username, role: data.role, is_admin: data.is_super_admin } // Ensure is_super_admin is included
      
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(user.value))
      
      return true
  }

  // const logout = () => {
  //   token.value = null
  //   user.value = null
  //   localStorage.removeItem('token')
  //   localStorage.removeItem('user')
  //   router.push('/login')
  // }
  const logout = async () => {
    try {
      // Ваш код для выхода (очистка токена и т.д.)
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login' // Fallback, если router не доступен
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  return { 
    token, 
    user, 
    isAuthenticated, 
    login, 
    logout 
  }
})