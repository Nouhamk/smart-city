# Guide d'intégration - Indice Météo Global

## Vue d'ensemble

L'indice météo global a été intégré dans la page **Paramètres et Historique** pour offrir une expérience utilisateur complète et cohérente. Cette intégration permet de visualiser, configurer et gérer l'indice météo depuis une seule interface.

## Sections principales

### 1. Section Indice Météo Actuel

**Localisation :** En haut de la page, sous le titre principal

**Fonctionnalités :**
- **Affichage de l'indice :** Valeur numérique avec niveau d'alerte coloré
- **Contributions des métriques :** Barres de progression montrant l'impact de chaque métrique
- **Dernière mise à jour :** Horodatage de la dernière calcul

**Utilisation :**
- Surveillez l'état actuel de l'indice météo global
- Identifiez rapidement les métriques qui contribuent le plus à l'indice
- Vérifiez la fraîcheur des données

### 2. Section Paramètres étendue

**Localisation :** Colonne de gauche, carte "Paramètres d'autorité"

**Nouvelles fonctionnalités :**

#### Seuils de l'indice météo
- **Seuil Critique :** Déclenche les alertes de niveau critique (défaut: 85)
- **Seuil Élevé :** Déclenche les alertes de niveau élevé (défaut: 70)

#### Poids des métriques
- **Température :** Impact de la température sur l'indice (défaut: 25%)
- **Humidité :** Impact de l'humidité (défaut: 20%)
- **Pression :** Impact de la pression atmosphérique (défaut: 15%)
- **Précipitations :** Impact des précipitations (défaut: 20%)
- **Vitesse du vent :** Impact du vent (défaut: 15%)
- **Visibilité :** Impact de la visibilité (défaut: 5%)

**Utilisation :**
- Ajustez les seuils selon vos besoins d'alerte
- Modifiez les poids pour refléter l'importance relative des métriques
- Les poids se normalisent automatiquement à 100%

### 3. Section Historique améliorée

**Localisation :** Colonne de droite, carte "Historique de l'indice météo"

**Fonctionnalités :**

#### Filtres
- **Niveau d'alerte :** Filtre par niveau (Faible, Moyen, Élevé, Critique)
- **Date début/fin :** Période d'analyse
- **Bouton Rechercher :** Applique les filtres

#### Tableau des données
- **Date :** Horodatage de la mesure
- **Indice :** Valeur numérique de l'indice
- **Niveau :** Badge coloré du niveau d'alerte
- **Métriques individuelles :** Température, humidité, pression, etc.
- **Actions :** Voir détails, voir alertes

#### Pagination
- Navigation entre les pages de résultats
- Affichage du nombre total d'enregistrements

### 4. Section Alertes Actives

**Localisation :** En bas de la page, carte "Alertes Actives"

**Fonctionnalités :**
- **Affichage des alertes :** Cartes colorées selon la sévérité
- **Actions rapides :**
  - **Acquitter :** Marquer comme vue (✓)
  - **Résoudre :** Marquer comme résolue (✓●)

**Utilisation :**
- Surveillez les alertes en temps réel
- Gérez le workflow des alertes
- Suivez l'historique des actions

## Workflow typique

### 1. Surveillance quotidienne
1. Consultez l'indice météo actuel en haut de page
2. Vérifiez les alertes actives en bas
3. Acquittez les alertes non critiques

### 2. Configuration des seuils
1. Ajustez les seuils critique et élevé selon vos besoins
2. Modifiez les poids des métriques si nécessaire
3. Sauvegardez les paramètres
4. Surveillez l'impact sur les alertes

### 3. Analyse historique
1. Définissez une période d'analyse
2. Filtrez par niveau d'alerte si nécessaire
3. Consultez les détails des métriques
4. Identifiez les tendances

### 4. Gestion des alertes
1. Consultez les alertes actives
2. Acquittez les alertes vues
3. Résolvez les alertes traitées
4. Suivez l'historique des actions

## Avantages de l'intégration

### Cohérence
- Interface unifiée pour toutes les fonctionnalités météo
- Design cohérent avec le reste de l'application
- Navigation intuitive

### Efficacité
- Accès rapide à toutes les informations météo
- Actions contextuelles depuis une seule page
- Filtrage et recherche avancés

### Flexibilité
- Configuration fine des seuils et poids
- Historique complet avec filtres
- Gestion complète du cycle de vie des alertes

## Points techniques

### API Endpoints utilisés
- `GET /api/weather-index/current/` - Indice actuel
- `GET /api/weather-index/history/` - Historique paginé
- `GET /api/weather-index/config/` - Configuration
- `PUT /api/weather-index/config/` - Mise à jour configuration
- `GET /api/weather-index/alerts/` - Alertes actives
- `PUT /api/weather-index/alerts/{id}/acknowledge/` - Acquittement
- `PUT /api/weather-index/alerts/{id}/resolve/` - Résolution

### Données utilisées
- **Prédictions réelles :** Données de la table "predictions" de Supabase
- **Métriques normalisées :** Température, humidité, pression, précipitations, vent, visibilité
- **Calcul horaire :** Indice recalculé automatiquement chaque heure

### Sécurité
- Authentification requise pour toutes les actions
- Validation des paramètres côté serveur
- Gestion des erreurs robuste

## Support

Pour toute question ou problème :
1. Consultez les logs de la console navigateur
2. Vérifiez la connectivité avec l'API backend
3. Contactez l'équipe de développement 