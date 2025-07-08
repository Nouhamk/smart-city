import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/api.service'

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isUser = computed(() => user.value?.role === 'user')
  const isPublic = computed(() => user.value?.role === 'public')
  const username = computed(() => user.value?.username || '')
  
  // Actions
  const login = async (username: string, password: string) => {
    loading.value = true
    error.value = null
    
    try {
      console.log('Tentative de connexion pour:', username)
      
      const response = await authService.login({ username, password })
      const { user: userData, access, refresh: refreshTokenValue, message } = response.data
      
      // Stocker les tokens et les données utilisateur
      token.value = access
      refreshToken.value = refreshTokenValue
      user.value = userData
      
      // Persister dans localStorage
      localStorage.setItem('token', access)
      localStorage.setItem('refresh_token', refreshTokenValue)
      localStorage.setItem('user', JSON.stringify(userData))
      localStorage.setItem('isAdmin', (userData.role === 'admin').toString())
      
      console.log('Connexion réussie:', message)
      return true
      
    } catch (err: any) {
      console.error('Erreur de connexion:', err)
      
      // Gérer les différents types d'erreurs
      if (err.response?.status === 401) {
        error.value = 'Identifiants invalides'
      } else if (err.response?.status === 400) {
        error.value = err.response?.data?.error || 'Données de connexion invalides'
      } else if (err.response?.status === 500) {
        error.value = 'Erreur serveur. Veuillez réessayer plus tard.'
      } else {
        error.value = 'Erreur de connexion. Vérifiez votre connexion internet.'
      }
      
      // Nettoyer les données en cas d'erreur
      clearAuthData()
      return false
      
    } finally {
      loading.value = false
    }
  }
  
  const register = async (userData: { 
    username: string, 
    email: string, 
    password: string, 
    role?: string 
  }) => {
    loading.value = true
    error.value = null
    
    try {
      console.log('Tentative d\'inscription pour:', userData.username)
      
      const response = await authService.register({
        ...userData,
        role: userData.role || 'user' // Rôle par défaut
      })
      
      const { user: newUser, access, refresh: refreshTokenValue, message } = response.data
      
      // Stocker les tokens et les données utilisateur
      token.value = access
      refreshToken.value = refreshTokenValue
      user.value = newUser
      
      // Persister dans localStorage
      localStorage.setItem('token', access)
      localStorage.setItem('refresh_token', refreshTokenValue)
      localStorage.setItem('user', JSON.stringify(newUser))
      localStorage.setItem('isAdmin', (newUser.role === 'admin').toString())
      
      console.log('Inscription réussie:', message)
      return true
      
    } catch (err: any) {
      console.error('Erreur d\'inscription:', err)
      
      if (err.response?.status === 400) {
        const errorData = err.response?.data
        if (errorData?.error === 'Username already exists') {
          error.value = 'Ce nom d\'utilisateur est déjà pris'
        } else if (errorData?.details) {
          // Gérer les erreurs de validation détaillées
          const validationErrors = Object.values(errorData.details).flat()
          error.value = validationErrors.join(', ')
        } else {
          error.value = errorData?.error || 'Données d\'inscription invalides'
        }
      } else if (err.response?.status === 500) {
        error.value = 'Erreur serveur. Veuillez réessayer plus tard.'
      } else {
        error.value = 'Erreur d\'inscription. Vérifiez votre connexion internet.'
      }
      
      return false
    } finally {
      loading.value = false
    }
  }
  
  const logout = async () => {
    loading.value = true
    
    try {
      // Appeler l'endpoint de déconnexion si on a un refresh token
      if (refreshToken.value) {
        await authService.logout(refreshToken.value)
      }
    } catch (err) {
      console.warn('Erreur lors de la déconnexion côté serveur:', err)
      // On continue le processus de déconnexion même en cas d'erreur
    } finally {
      // Nettoyer les données locales dans tous les cas
      clearAuthData()
      loading.value = false
    }
  }
  
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      throw new Error('Aucun refresh token disponible')
    }
    
    try {
      const response = await authService.refreshToken(refreshToken.value)
      const { access } = response.data
      
      token.value = access
      localStorage.setItem('token', access)
      
      return access
    } catch (err) {
      console.error('Erreur lors du rafraîchissement du token:', err)
      // Si le refresh token est invalide, déconnecter l'utilisateur
      clearAuthData()
      throw err
    }
  }
  
  const clearAuthData = () => {
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    localStorage.removeItem('isAdmin')
  }
  
  // Initialiser l'état depuis localStorage
  const initializeAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUser = localStorage.getItem('user')
    
    if (storedToken && storedRefreshToken && storedUser) {
      try {
        token.value = storedToken
        refreshToken.value = storedRefreshToken
        user.value = JSON.parse(storedUser)
      } catch (err) {
        console.error('Erreur lors de la restauration des données d\'authentification:', err)
        clearAuthData()
      }
    }
  }
  
  // Vérifier si le token est valide (optionnel - peut être fait avec un endpoint /me)
  const checkAuthStatus = async () => {
    if (!token.value) return false
    
    try {
      return true
    } catch (err) {
      console.error('Token invalide:', err)
      clearAuthData()
      return false
    }
  }
  
  // Initialiser lors de la création du store
  initializeAuth()
  
  return {
    // State
    user,
    token,
    refreshToken,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    isUser,
    isPublic,
    username,
    
    // Actions
    login,
    register,
    logout,
    refreshAccessToken,
    clearAuthData,
    checkAuthStatus
  }
})