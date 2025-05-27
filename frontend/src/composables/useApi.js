import { ref } from 'vue'
import { useAuthStore } from '@/store/auth'

export const useApi = () => {
  const authStore = useAuthStore()
  const baseUrl = '/api';
  const error = ref(null)
  const loading = ref(false)

  const fetchApi = async (endpoint, options = {}) => {
    loading.value = true
    error.value = null
    
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      }
      
      if (authStore.token) {
        headers['Authorization'] = `Bearer ${authStore.token}`
      }

      console.log(baseUrl)      
      const response = await fetch(`${baseUrl}${endpoint}`, {
        ...options,
        headers,
        credentials: 'include'  // Измените на 'include'
      })

      const data = await response.json().catch(() => ({}));
      
      if (!response.ok) { // Добавляем проверку на !response.ok здесь
        const errorData = data;
        // Вместо создания новой ошибки, выбрасываем объект с response и errorData
        const error = new Error(errorData.message || response.statusText);
        error.response = response; // Добавляем исходный response
        error.response.data = errorData; // Добавляем распарсенные данные ошибки
        throw error;
      }
      return data;
    } catch (err) {
      console.error("Error in fetchApi:", err); // Добавим для отладки в useApi
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    fetchApi, error, loading
  }
}
