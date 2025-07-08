<template>
  <header>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <router-link class="navbar-brand" to="/">Smart City</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Accueil</router-link>
            </li>
            <li class="nav-item" v-if="authStore.isAuthenticated">
              <router-link class="nav-link" to="/dashboard">Tableau de bord</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/map">Carte</router-link>
            </li>
            <li class="nav-item" v-if="authStore.isAdmin">
              <router-link class="nav-link" to="/history">Paramètres & Historique</router-link>
            </li>
          </ul>
          <div class="d-flex">
            <ul class="navbar-nav">
              <!-- Menu pour utilisateurs non connectés -->
              <li class="nav-item" v-if="!authStore.isAuthenticated">
                <router-link class="nav-link" to="/login">Connexion</router-link>
              </li>
              <li class="nav-item" v-if="!authStore.isAuthenticated">
                <router-link class="nav-link" to="/register">Inscription</router-link>
              </li>
              
              <!-- Menu pour utilisateurs connectés -->
              <li class="nav-item dropdown" v-if="authStore.isAuthenticated">
                <a 
                  class="nav-link dropdown-toggle d-flex align-items-center" 
                  href="#" 
                  id="navbarDropdown" 
                  role="button" 
                  data-bs-toggle="dropdown" 
                  aria-expanded="false"
                  @click="toggleDropdown"
                >
                  <i class="bi bi-person-circle me-2"></i>
                  {{ authStore.username }}
                </a>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
                  <!-- Header du menu -->
                  <li>
                    <div class="dropdown-header">
                      <div class="fw-bold">{{ authStore.username }}</div>
                      <small class="text-muted">{{ getUserRoleLabel() }}</small>
                    </div>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  
                  <!-- Options du menu -->
                  <li>
                    <router-link class="dropdown-item" to="/profile">
                      <i class="bi bi-person me-2"></i>
                      Mon Profil
                    </router-link>
                  </li>
                  
                  <!-- Options admin uniquement -->
                  <li v-if="authStore.isAdmin">
                    <router-link class="dropdown-item" to="/history">
                      <i class="bi bi-gear me-2"></i>
                      Paramètres & Historique
                    </router-link>
                  </li>
                  
                  <li><hr class="dropdown-divider"></li>
                  
                  <!-- Déconnexion -->
                  <li>
                    <button class="dropdown-item text-danger" @click="handleLogout">
                      <i class="bi bi-box-arrow-right me-2"></i>
                      Déconnexion
                    </button>
                  </li>
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
import { useAuthStore } from './store/auth'

export default defineComponent({
  name: 'App',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const isDropdownOpen = ref(false)
    
    const toggleDropdown = () => {
      isDropdownOpen.value = !isDropdownOpen.value
    }
    
    const getUserRoleLabel = () => {
      if (authStore.isAdmin) return 'Administrateur'
      if (authStore.isUser) return 'Utilisateur'
      return 'Public'
    }
    
    const handleLogout = async () => {
      try {
        await authStore.logout()
        isDropdownOpen.value = false
        router.push('/login')
        console.log('Déconnexion réussie')
      } catch (error) {
        console.error('Erreur lors de la déconnexion:', error)
      }
    }
    
    return {
      authStore,
      isDropdownOpen,
      toggleDropdown,
      getUserRoleLabel,
      handleLogout
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

/* Styles pour le menu utilisateur */
.navbar-brand {
  font-weight: bold;
  text-decoration: none !important;
}

.nav-link {
  transition: color 0.15s ease-in-out;
}

.nav-link:hover {
  color: rgba(255, 255, 255, 0.8) !important;
}

.nav-link.router-link-active {
  color: white !important;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 0.375rem;
}

.dropdown-menu {
  min-width: 200px;
  border: none;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  border-radius: 0.5rem;
  padding: 0.5rem 0;
}

.dropdown-header {
  padding: 0.5rem 1rem;
  color: #495057;
}

.dropdown-item {
  padding: 0.5rem 1rem;
  transition: background-color 0.15s ease-in-out;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-item.text-danger:hover {
  background-color: #f8d7da;
  color: #721c24 !important;
}

.dropdown-divider {
  margin: 0.5rem 0;
}

/* Animation pour le dropdown */
.dropdown-menu {
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity 0.15s ease, transform 0.15s ease;
  pointer-events: none;
}

.dropdown-menu.show {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
</style>