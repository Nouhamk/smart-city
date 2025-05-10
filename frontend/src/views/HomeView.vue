<template>
  <div class="home">
    <div class="jumbotron text-center">
      <h1 class="display-4">Smart City & Environnement</h1>
      <p class="lead">Bienvenue sur notre plateforme de suivi environnemental et de prédiction pour une ville intelligente.</p>
      <hr class="my-4">
      <p>Consultez les données environnementales en temps réel, les prédictions et les alertes.</p>
      <router-link to="/dashboard" class="btn btn-primary btn-lg">Accéder au tableau de bord</router-link>
    </div>
    
    <div class="row mt-5">
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Données en temps réel</h5>
            <p class="card-text">Consultez les mesures environnementales actuelles : pollution, météo, trafic...</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Prédictions</h5>
            <p class="card-text">Anticipez les évolutions de la qualité de l'air et des conditions météorologiques.</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Alertes</h5>
            <p class="card-text">Recevez des notifications en cas de pic de pollution ou d'événement inhabituel.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'HomeView'
})
</script>
