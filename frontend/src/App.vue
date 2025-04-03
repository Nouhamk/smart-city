<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <a class="navbar-brand" href="#">Smart City</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Accueil</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">Tableau de bord</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/map">Carte</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/history">Historique</router-link>
            </li>
          </ul>
          <div class="d-flex">
            <ul class="navbar-nav">
              <li class="nav-item" v-if="!isLoggedIn">
                <router-link class="nav-link" to="/login">Connexion</router-link>
              </li>
              <li class="nav-item" v-if="!isLoggedIn">
                <router-link class="nav-link" to="/register">Inscription</router-link>
              </li>
              <li class="nav-item dropdown" v-if="isLoggedIn">
                <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                  {{ username }}
                </a>
                <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
                  <li><router-link class="dropdown-item" to="/profile">Profil</router-link></li>
                  <li><router-link class="dropdown-item" to="/settings">Paramètres</router-link></li>
                  <li><hr class="dropdown-divider"></li>
                  <li><a class="dropdown-item" href="#" @click.prevent="logout">Déconnexion</a></li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
  </header>

  <main class="container mt-4">
    <router-view/>
  </main>

  <footer class="bg-light text-center text-lg-start mt-5">
    <div class="text-center p-3" style="background-color: rgba(0, 0, 0, 0.05);">
      © {{ new Date().getFullYear() }} Smart City & Environnement
    </div>
  </footer>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'App',
  setup() {
    const isLoggedIn = ref(false)
    const username = ref('Utilisateur')
    const router = useRouter()
    
    const logout = () => {
      // Fonction de déconnexion à implémenter
      console.log('Déconnexion')
      isLoggedIn.value = false
      // Rediriger vers la page d'accueil
      router.push('/')
    }
    
    return {
      isLoggedIn,
      username,
      logout
    }
  }
})
</script>

<style>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
}
</style>