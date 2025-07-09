# Système d'Indice Météo Global

## Vue d'ensemble

Le système d'indice météo global calcule un indicateur composite basé sur plusieurs métriques météorologiques pour évaluer les conditions environnementales d'une région. Cet indice est utilisé pour déclencher des alertes automatiques et fournir une vue d'ensemble des conditions météorologiques.

## Architecture

### Composants principaux

1. **WeatherIndexCalculator** : Calcule l'indice météo global
2. **WeatherIndexAlertService** : Gère les alertes basées sur l'indice
3. **WeatherIndexScheduler** : Planifie le recalcul automatique
4. **API Routes** : Endpoints REST pour accéder aux données

### Métriques prises en compte

| Métrique | Poids | Description |
|----------|-------|-------------|
| Température | 25% | Impact sur le confort et la santé |
| Humidité | 20% | Qualité de l'air et confort |
| Pression | 15% | Stabilité atmosphérique |
| Précipitations | 15% | Risques d'inondation et visibilité |
| Vitesse du vent | 10% | Risques de dommages |
| Visibilité | 10% | Sécurité routière |
| Couverture nuageuse | 5% | Impact sur l'ensoleillement |

## Calcul de l'indice

### 1. Normalisation

Chaque métrique est normalisée entre 0 et 1 en utilisant :
- **Normalisation Min-Max** : `(valeur - min) / (max - min)`
- **Fonction gaussienne** : Pénalise les écarts par rapport aux valeurs optimales

### 2. Pondération

L'indice final est calculé comme :
```
Indice = Σ(normalisé_i × poids_i)
```

### 3. Niveaux d'alerte

| Niveau | Seuil | Description |
|--------|-------|-------------|
| Low | < 0.3 | Conditions normales |
| Medium | 0.3 - 0.5 | Attention requise |
| High | 0.5 - 0.7 | Alerte active |
| Critical | > 0.8 | Alerte critique |

## API Endpoints

### GET /api/weather-index/
Récupère l'indice météo actuel pour toutes les régions ou des régions spécifiques.

**Paramètres :**
- `regions` (optionnel) : Liste des régions séparées par des virgules

**Réponse :**
```json
[
  {
    "index": 0.346,
    "level": "low",
    "region": "Paris",
    "timestamp": "2025-07-09T20:05:13.583309",
    "details": {
      "temperature": {
        "raw_value": 28.5,
        "normalized": 0.515,
        "weight": 0.25,
        "contribution": 0.129
      }
    }
  }
]
```

### GET /api/weather-index/history/
Récupère l'historique de l'indice météo pour une région.

**Paramètres :**
- `region` (requis) : Nom de la région
- `hours` (optionnel) : Nombre d'heures d'historique (défaut: 24)

### GET /api/weather-index/config/
Récupère la configuration du système (poids, seuils, valeurs de référence).

## Utilisation

### Backend

```python
from data_api.weather_index.weather_index_calculator import weather_index_calculator

# Calculer l'indice pour des données météo
weather_data = {
    'temperature': 28.5,
    'humidity': 75.0,
    'pressure': 1010.0,
    'precipitation': 5.0,
    'wind_speed': 25.0,
    'visibility': 8.0,
    'cloud_cover': 60.0
}

result = weather_index_calculator.calculate_weather_index(weather_data, "Paris")
print(f"Indice: {result['index']:.3f} - Niveau: {result['level']}")
```

### Frontend

```typescript
import { weatherIndexService } from '@/services/weatherIndexService';

// Récupérer l'indice actuel
const weatherIndices = await weatherIndexService.getCurrentWeatherIndex(['Paris', 'Lyon']);

// Récupérer l'historique
const history = await weatherIndexService.getWeatherIndexHistory('Paris', 48);
```

## Planification automatique

Le système recalcule automatiquement l'indice toutes les heures et vérifie les alertes :

```python
from data_api.weather_index.scheduler import weather_index_scheduler

# Démarrer le planificateur
weather_index_scheduler.start()

# Arrêter le planificateur
weather_index_scheduler.stop()
```

## Configuration

### Modifier les poids

```python
calculator = WeatherIndexCalculator()
calculator.weights['temperature'] = 0.30  # Augmenter le poids de la température
calculator.weights['humidity'] = 0.15     # Diminuer le poids de l'humidité
```

### Modifier les seuils d'alerte

```python
calculator.alert_thresholds['high'] = 0.6  # Seuil d'alerte plus strict
```

### Modifier les valeurs de référence

```python
calculator.reference_values['temperature'] = {
    'min': -5,
    'max': 35,
    'optimal': 22
}
```

## Tests

Exécuter les tests :

```bash
cd backend
python test_weather_index_simple.py
```

## Intégration avec le système d'alertes

Le système d'indice météo s'intègre automatiquement avec le système d'alertes existant :

- Création d'alertes automatiques basées sur l'indice
- Mise à jour des alertes existantes
- Résolution automatique quand les conditions s'améliorent

## Monitoring

Le système génère des logs détaillés pour le monitoring :

- Calculs d'indice
- Création/mise à jour d'alertes
- Erreurs et exceptions

## Dépendances

- `numpy` : Calculs mathématiques
- `pandas` : Manipulation de données
- `django` : Framework web
- `djangorestframework` : API REST
- `supabase` : Base de données 