import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { User } from '../types/models'
import { authService } from '../services/api.service'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.isStaff === true)
  const username = computed(() => user.value?.username || '')
  
  // Actions
  const login = async (username: string, password: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.login({ username, password })
      token.value = response.data.access
      localStorage.setItem('token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      
      // Charger les informations utilisateur
      await loadUserProfile()
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Erreur de connexion'
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      return false
    } finally {
      loading.value = false
    }
  }
  
  const register = async (userData: { username: string, email: string, password: string }) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.register(userData)
      token.value = response.data.access
      localStorage.setItem('token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      
      // Charger les informations utilisateur
      await loadUserProfile()
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Erreur d\'inscription'
      return false
    } finally {
      loading.value = false
    }
  }
  
  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
  }
  
  const loadUserProfile = async () => {
    if (!token.value) return
    
    loading.value = true
    
    try {
      const response = await authService.getProfile()
      user.value = response.data
    } catch (err: any) {
      error.value = 'Impossible de charger le profil utilisateur'
      // Si erreur 401, déconnecter l'utilisateur
      if (err.response?.status === 401) {
        logout()
      }
    } finally {
      loading.value = false
    }
  }
  
  // Initialiser - charger le profil si un token est présent
  if (token.value) {
    loadUserProfile()
  }
  
  return {
    // State
    user,
    token,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    username,
    
    // Actions
    login,
    register,
    logout,
    loadUserProfile
  }
})
