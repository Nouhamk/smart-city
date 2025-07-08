import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { User } from '../types/models'
import { authService } from '../services/api.service'

interface AuthResponse {
  refresh: string;
  access: string;
  user?: User;
  roles?: string[];
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const roles = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => roles.value.includes('ADMIN'))
  const username = computed(() => user.value?.username || '')
  
  // Actions
  const login = async (username: string, password: string) => {
    loading.value = true
    error.value = null
    
    try {
      // Demo login handling
      if (username === 'admin' && password === 'admin') {
        token.value = 'demo-token'
        roles.value = ['ADMIN']
        user.value = {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          isStaff: true
        }
        localStorage.setItem('token', token.value)
        localStorage.setItem('roles', JSON.stringify(roles.value))
        localStorage.setItem('isAdmin', 'true')
        return true
      }

      // Regular API login
      const response = await authService.login({ username, password })
      token.value = response.data.access
      localStorage.setItem('token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      
      // Set default role if none provided
      const userRoles = response.data.roles || ['USER']
      roles.value = userRoles
      localStorage.setItem('roles', JSON.stringify(userRoles))
      localStorage.setItem('isAdmin', userRoles.includes('ADMIN').toString())
      
      await loadUserProfile()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Erreur de connexion'
      token.value = null
      roles.value = []
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('roles')
      localStorage.removeItem('isAdmin')
      return false
    } finally {
      loading.value = false
    }
  }
  
  const register = async (userData: { username: string, email: string, password: string, role: string }) => {
    loading.value = true
    error.value = null
    
    try {
      // Demo registration
      const userRole = userData.role || 'USER'
      localStorage.setItem('roles', JSON.stringify([userRole]))
      localStorage.setItem('isAdmin', (userRole === 'ADMIN').toString())

      // In production, use this:
      // const response = await authService.register(userData)
      // token.value = response.data.access
      // localStorage.setItem('token', response.data.access)
      // localStorage.setItem('refresh_token', response.data.refresh)
      // await loadUserProfile()
      
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
    roles.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('roles')
    localStorage.removeItem('isAdmin')
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
  
  // Improved role initialization
  const initializeAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedRoles = localStorage.getItem('roles')
    const isAdmin = localStorage.getItem('isAdmin')

    if (storedToken) {
      token.value = storedToken
    }
    
    if (storedRoles) {
      try {
        roles.value = JSON.parse(storedRoles)
      } catch {
        roles.value = ['USER'] // Fallback role
        localStorage.setItem('roles', JSON.stringify(roles.value))
      }
    }

    // Ensure admin flag is in sync
    if (isAdmin === 'true' && !roles.value.includes('ADMIN')) {
      roles.value.push('ADMIN')
      localStorage.setItem('roles', JSON.stringify(roles.value))
    }
  }
  
  // Call initialize on store creation
  initializeAuth()
  
  // Initialiser - charger le profil si un token est présent
  if (token.value) {
    loadUserProfile()
  }
  
  return {
    // State
    user,
    token,
    roles,
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
