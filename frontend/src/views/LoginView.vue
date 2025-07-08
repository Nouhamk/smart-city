<template>
  <div class="login">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-center">Connexion</h3>
          </div>
          <div class="card-body">
            <!-- Affichage des erreurs -->
            <div v-if="authStore.error" class="alert alert-danger" role="alert">
              {{ authStore.error }}
            </div>
            
            <!-- Formulaire de connexion -->
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Nom d'utilisateur</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="username" 
                  v-model="username" 
                  required
                  :disabled="authStore.loading"
                  :class="{ 'is-invalid': submitted && !username }"
                >
                <div v-if="submitted && !username" class="invalid-feedback">
                  Le nom d'utilisateur est requis
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
                  :disabled="authStore.loading"
                  :class="{ 'is-invalid': submitted && !password }"
                >
                <div v-if="submitted && !password" class="invalid-feedback">
                  Le mot de passe est requis
                </div>
              </div>
              
              <div class="d-grid gap-2">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="authStore.loading"
                >
                  <span v-if="authStore.loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Se connecter
                </button>
              </div>
            </form>
            
            <div class="text-center mt-3">
              <p>Pas encore de compte ? <router-link to="/register">S'inscrire</router-link></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

export default defineComponent({
  name: 'LoginView',
  setup() {
    const username = ref('')
    const password = ref('')
    const submitted = ref(false)
    const router = useRouter()
    const authStore = useAuthStore()
    
    const handleLogin = async () => {
      submitted.value = true
      
      // Validation côté client
      if (!username.value.trim() || !password.value.trim()) {
        authStore.error = 'Veuillez remplir tous les champs'
        return
      }
      
      try {
        const success = await authStore.login(username.value.trim(), password.value)
        
        if (success) {
          console.log('Connexion réussie, redirection vers le dashboard')
          router.push('/dashboard')
        }
        // L'erreur est déjà gérée dans le store
      } catch (error) {
        console.error('Erreur inattendue lors de la connexion:', error)
      }
    }
    
    return {
      username,
      password,
      submitted,
      authStore,
      handleLogin
    }
  }
})
</script>

<style scoped>
.login {
  padding: 20px 0;
}

.card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f8f9fa;
}
</style>