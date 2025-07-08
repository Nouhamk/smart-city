<template>
  <div class="register">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-center">Inscription</h3>
          </div>
          <div class="card-body">
            <!-- Affichage des erreurs -->
            <div v-if="errorMessage" class="alert alert-danger" role="alert">
              {{ errorMessage }}
            </div>
            
            <!-- Message de succès -->
            <div v-if="successMessage" class="alert alert-success" role="alert">
              {{ successMessage }}
            </div>
            
            <form @submit.prevent="register">
              <div class="mb-3">
                <label for="username" class="form-label">Nom d'utilisateur</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="username" 
                  v-model="username" 
                  required
                  :disabled="isLoading"
                  :class="{ 'is-invalid': submitted && !username }"
                >
                <div v-if="submitted && !username" class="invalid-feedback">
                  Le nom d'utilisateur est requis
                </div>
              </div>
              
              <div class="mb-3">
                <label for="email" class="form-label">Adresse e-mail</label>
                <input 
                  type="email" 
                  class="form-control" 
                  id="email" 
                  v-model="email" 
                  required
                  :disabled="isLoading"
                  :class="{ 'is-invalid': submitted && !isValidEmail }"
                >
                <div v-if="submitted && !isValidEmail" class="invalid-feedback">
                  Une adresse e-mail valide est requise
                </div>
              </div>
              
              <div class="mb-3">
                <label for="password" class="form-label">Mot de passe</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="password" 
                  v-model="password" 
                  required
                  :disabled="isLoading"
                  :class="{ 'is-invalid': submitted && !password }"
                >
                <div v-if="submitted && !password" class="invalid-feedback">
                  Le mot de passe est requis
                </div>
              </div>
              
              <div class="mb-3">
                <label for="role" class="form-label">Rôle</label>
                <select 
                  class="form-select" 
                  id="role" 
                  v-model="role"
                  required
                  :disabled="isLoading"
                  :class="{ 'is-invalid': submitted && !role }"
                >
                  <option value="">Sélectionner un rôle</option>
                  <option value="user">Utilisateur</option>
                  <option value="admin">Administrateur</option>
                </select>
                <div v-if="submitted && !role" class="invalid-feedback">
                  Le rôle est requis
                </div>
              </div>
              
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirmer le mot de passe</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="confirmPassword" 
                  v-model="confirmPassword" 
                  required
                  :disabled="isLoading"
                  :class="{ 'is-invalid': submitted && !passwordsMatch }"
                >
                <div v-if="submitted && !passwordsMatch" class="invalid-feedback">
                  Les mots de passe ne correspondent pas
                </div>
              </div>
              
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary" :disabled="isLoading">
                  <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ isLoading ? 'Inscription en cours...' : 'S\'inscrire' }}
                </button>
              </div>
            </form>
            
            <div class="text-center mt-3">
              <p>Déjà inscrit ? <router-link to="/login">Se connecter</router-link></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '../services/api.service'

export default defineComponent({
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    
    // État du formulaire
    const username = ref('')
    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const role = ref('')
    const errorMessage = ref('')
    const successMessage = ref('')
    const isLoading = ref(false)
    const submitted = ref(false)
    
    // Validation
    const isValidEmail = computed(() => {
      if (!email.value) return false
      return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)
    })
    
    const passwordsMatch = computed(() => {
      return password.value === confirmPassword.value
    })
    
    // Inscription
    const register = async () => {
      submitted.value = true
      errorMessage.value = ''
      successMessage.value = ''
      
      // Validation côté client
      if (!username.value || !email.value || !password.value || !confirmPassword.value || !role.value) {
        errorMessage.value = 'Tous les champs sont requis'
        return
      }
      
      if (!isValidEmail.value) {
        errorMessage.value = 'Format d\'e-mail invalide'
        return
      }
      
      if (password.value.length < 8) {
        errorMessage.value = 'Le mot de passe doit contenir au moins 8 caractères'
        return
      }
      
      if (!passwordsMatch.value) {
        errorMessage.value = 'Les mots de passe ne correspondent pas'
        return
      }
      
      try {
        isLoading.value = true
        
        console.log('🚀 Tentative d\'inscription:', {
          username: username.value,
          email: email.value,
          role: role.value
        })
        
        // Appel API d'inscription
        const response = await authService.register({
          username: username.value,
          email: email.value,
          password: password.value,
          role: role.value
        })
        
        console.log('✅ Inscription réussie:', response.data)
        
        // Afficher le message de succès
        successMessage.value = 'Inscription réussie ! Redirection vers la connexion...'
        
        // Redirection après 2 secondes
        setTimeout(() => {
          router.push('/login')
        }, 2000)
        
      } catch (error: any) {
        console.error('❌ Erreur d\'inscription:', error)
        
        // Gestion des erreurs spécifiques
        if (error.response?.status === 400) {
          const errorData = error.response?.data
          
          if (errorData?.error === 'Username already exists') {
            errorMessage.value = 'Ce nom d\'utilisateur est déjà pris'
          } else if (errorData?.details) {
            // Gestion des erreurs de validation détaillées
            const validationErrors = Object.values(errorData.details).flat() as string[]
            errorMessage.value = validationErrors.join(', ')
          } else {
            errorMessage.value = errorData?.error || 'Données d\'inscription invalides'
          }
        } else if (error.response?.status === 500) {
          errorMessage.value = 'Erreur serveur. Veuillez réessayer plus tard.'
        } else if (error.message?.includes('Network Error')) {
          errorMessage.value = 'Impossible de contacter le serveur. Vérifiez votre connexion.'
        } else {
          errorMessage.value = 'Une erreur est survenue lors de l\'inscription'
        }
      } finally {
        isLoading.value = false
      }
    }
    
    return {
      username,
      email,
      password,
      confirmPassword,
      role,
      errorMessage,
      successMessage,
      isLoading,
      submitted,
      isValidEmail,
      passwordsMatch,
      register
    }
  }
})
</script>

<style scoped>
.register {
  padding: 20px 0;
}

.card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f8f9fa;
}

.alert {
  border-radius: 4px;
  border: 1px solid transparent;
}

.alert-danger {
  background-color: #f8d7da;
  border-color: #f5c2c7;
  color: #842029;
}

.alert-success {
  background-color: #d1e7dd;
  border-color: #badbcc;
  color: #0f5132;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}
</style>