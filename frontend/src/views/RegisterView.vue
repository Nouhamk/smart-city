<template>
    <div class="register">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h3 class="text-center">Inscription</h3>
            </div>
            <div class="card-body">
              <div v-if="errorMessage" class="alert alert-danger" role="alert">
                {{ errorMessage }}
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
                    :class="{ 'is-invalid': submitted && !password }"
                  >
                  <div v-if="submitted && !password" class="invalid-feedback">
                    Le mot de passe est requis
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
                    :class="{ 'is-invalid': submitted && !passwordsMatch }"
                  >
                  <div v-if="submitted && !passwordsMatch" class="invalid-feedback">
                    Les mots de passe ne correspondent pas
                  </div>
                </div>
                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-primary" :disabled="isLoading">
                    <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    S'inscrire
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
  
  export default defineComponent({
    name: 'RegisterView',
    setup() {
      // Router
      const router = useRouter()
      
      // Reactive state
      const username = ref('')
      const email = ref('')
      const password = ref('')
      const confirmPassword = ref('')
      const errorMessage = ref('')
      const isLoading = ref(false)
      const submitted = ref(false)
      
      // Computed properties
      const isValidEmail = computed(() => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)
      })
      
      const passwordsMatch = computed(() => {
        return password.value === confirmPassword.value
      })
      
      // Methods
      const register = async () => {
        submitted.value = true
        errorMessage.value = ''
        
        // Basic validation
        if (!username.value || !email.value || !password.value || !confirmPassword.value) {
          errorMessage.value = 'Tous les champs sont requis'
          return
        }
        
        if (!isValidEmail.value) {
          errorMessage.value = 'Format d\'e-mail invalide'
          return
        }
        
        if (!passwordsMatch.value) {
          errorMessage.value = 'Les mots de passe ne correspondent pas'
          return
        }
        
        try {
          isLoading.value = true
          
          // Simulate API call - replace with your actual API call
          // const response = await authService.register({
          //  username: username.value,
          //  email: email.value,
          //  password: password.value,
          // })
          
          // For demonstration purposes, we'll just wait 1 second
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          // Show success and redirect
          alert('Inscription réussie ! Veuillez vous connecter.')
          router.push('/login')
        } catch (error: any) {
          errorMessage.value = error?.response?.data?.message || 'Une erreur est survenue lors de l\'inscription'
        } finally {
          isLoading.value = false
        }
      }
      
      return {
        username,
        email,
        password,
        confirmPassword,
        errorMessage,
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
  </style>