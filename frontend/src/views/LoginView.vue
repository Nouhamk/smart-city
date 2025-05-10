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
import { authService } from '../services/api.service'

export default defineComponent({
  name: 'LoginView',
  setup() {
    const username = ref('')
    const password = ref('')
    const router = useRouter()
    
    const login = async () => {
      try {
        //const response = await authService.login({
          //username: username.value,
          //password: password.value
        //})
        
        // Stocker le token JWT
        //localStorage.setItem('token', response.data.access)
        //localStorage.setItem('refresh_token', response.data.refresh)
        
        localStorage.setItem('token', 'fake-jwt-token');
        localStorage.setItem('refresh_token', 'fake-refresh-token');
        // Rediriger vers le tableau de bord
        router.push('/dashboard')
      } catch (error) {
        console.error('Erreur de connexion', error)
        alert('Identifiants invalides')
      }
    }
    
    return {
      username,
      password,
      login
    }
  }
})
</script>
