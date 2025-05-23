<template>
  <div class="login">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-center">Connexion</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="login">
              <div class="mb-3">
                <label for="username" class="form-label">Nom d'utilisateur</label>
                <input type="text" class="form-control" id="username" v-model="username" required>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Mot de passe</label>
                <input type="password" class="form-control" id="password" v-model="password" required>
              </div>
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary">Se connecter</button>
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
    const router = useRouter()
    const authStore = useAuthStore()
    const error = ref('')
    
    const login = async () => {
      try {
        // For demo purposes, simulating different user roles
        if (username.value === 'admin' && password.value === 'admin') {
          // Simulate admin login
          localStorage.setItem('token', 'fake-jwt-token')
          localStorage.setItem('refresh_token', 'fake-refresh-token')
          localStorage.setItem('roles', JSON.stringify(['ADMIN']))
          localStorage.setItem('isAdmin', 'true')
          router.push('/dashboard')
        } else if (username.value && password.value) {
          // Simulate regular user login
          localStorage.setItem('token', 'fake-jwt-token')
          localStorage.setItem('refresh_token', 'fake-refresh-token')
          localStorage.setItem('roles', JSON.stringify(['USER']))
          localStorage.setItem('isAdmin', 'false')
          router.push('/dashboard')
        }
        
        /* In production, use this instead:
        const success = await authStore.login(username.value, password.value)
        if (success) {
          router.push('/dashboard')
        } else {
          error.value = 'Identifiants invalides'
        }
        */
      } catch (err) {
        console.error('Erreur de connexion', err)
        error.value = 'Identifiants invalides'
      }
    }
    
    return {
      username,
      password,
      login,
      error
    }
  }
})
</script>
