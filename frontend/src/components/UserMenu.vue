<!-- components/UserMenu.vue -->
<template>
  <div class="user-menu">
    <!-- Menu utilisateur connecté -->
    <div v-if="authStore.isAuthenticated" class="dropdown">
      <button
        class="btn btn-link dropdown-toggle user-button"
        type="button"
        id="userDropdown"
        data-bs-toggle="dropdown"
        aria-expanded="false"
        @click="toggleDropdown"
      >
        <i class="bi bi-person-circle me-2"></i>
        {{ authStore.username }}
      </button>
      
      <ul 
        class="dropdown-menu dropdown-menu-end"
        :class="{ show: isDropdownOpen }"
        aria-labelledby="userDropdown"
      >
        <li>
          <div class="dropdown-header">
            <div class="fw-bold">{{ authStore.username }}</div>
            <small class="text-muted">{{ getUserRoleLabel() }}</small>
          </div>
        </li>
        <li><hr class="dropdown-divider"></li>
        
        <!-- Options pour tous les utilisateurs -->
        <li>
          <router-link class="dropdown-item" to="/profile" @click="closeDropdown">
            <i class="bi bi-person me-2"></i>
            Mon Profil
          </router-link>
        </li>
        
        <!-- Options admin uniquement -->
        <li v-if="authStore.isAdmin">
          <router-link class="dropdown-item" to="/history" @click="closeDropdown">
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
    </div>
    
    <!-- Liens pour utilisateurs non connectés -->
    <div v-else class="auth-links">
      <router-link to="/login" class="btn btn-outline-light me-2">
        Connexion
      </router-link>
      <router-link to="/register" class="btn btn-light">
        Inscription
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

export default defineComponent({
  name: 'UserMenu',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const isDropdownOpen = ref(false)
    
    const toggleDropdown = () => {
      isDropdownOpen.value = !isDropdownOpen.value
    }
    
    const closeDropdown = () => {
      isDropdownOpen.value = false
    }
    
    const getUserRoleLabel = () => {
      if (authStore.isAdmin) return 'Administrateur'
      if (authStore.isUser) return 'Utilisateur'
      return 'Public'
    }
    
    const handleLogout = async () => {
      try {
        await authStore.logout()
        closeDropdown()
        router.push('/login')
      } catch (error) {
        console.error('Erreur lors de la déconnexion:', error)
      }
    }
    
    // Fermer le dropdown si on clique ailleurs
    const handleClickOutside = (event: Event) => {
      const dropdown = document.getElementById('userDropdown')
      if (dropdown && !dropdown.contains(event.target as Node)) {
        closeDropdown()
      }
    }
    
    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })
    
    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })
    
    return {
      authStore,
      isDropdownOpen,
      toggleDropdown,
      closeDropdown,
      getUserRoleLabel,
      handleLogout
    }
  }
})
</script>

<style scoped>
.user-menu {
  position: relative;
}

.user-button {
  color: white !important;
  text-decoration: none !important;
  border: none;
  background: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: background-color 0.15s ease-in-out;
}

.user-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white !important;
}

.user-button:focus {
  box-shadow: 0 0 0 0.25rem rgba(255, 255, 255, 0.25);
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

.auth-links .btn {
  border-radius: 0.375rem;
  padding: 0.5rem 1rem;
  font-weight: 500;
}

.btn-outline-light:hover {
  background-color: white;
  color: #0d6efd;
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

---

<!-- App.vue ou votre composant de navigation principal -->
<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/">Smart City</router-link>
        
        <!-- Menu de navigation principal -->
        <div class="navbar-nav me-auto">
          <router-link class="nav-link" to="/">Accueil</router-link>
          <router-link v-if="authStore.isAuthenticated" class="nav-link" to="/dashboard">
            Tableau de bord
          </router-link>
          <router-link class="nav-link" to="/map">Carte</router-link>
          <router-link 
            v-if="authStore.isAdmin" 
            class="nav-link" 
            to="/history"
          >
            Paramètres & Historique
          </router-link>
        </div>
        
        <!-- Menu utilisateur -->
        <UserMenu />
      </div>
    </nav>
    
    <main>
      <router-view />
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useAuthStore } from './store/auth'
import UserMenu from './components/UserMenu.vue'

export default defineComponent({
  name: 'App',
  components: {
    UserMenu
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      authStore
    }
  }
})
</script>

<style>
/* Styles globaux pour l'application */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.navbar-brand {
  font-weight: bold;
  font-size: 1.5rem;
}

.nav-link {
  font-weight: 500;
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

main {
  min-height: calc(100vh - 56px); /* Hauteur navbar */
}
</style>