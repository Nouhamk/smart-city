# Documentation d'intégration API pour le Frontend (Smart City)

## 1. Authentification & Utilisateurs

### a. Enregistrement (Register)
- **Endpoint** : `POST /api/auth/register/`
- **Payload exemple** :
```json
{
  "username": "john",
  "password": "motdepasse",
  "email": "john@example.com",
  "role": "user"  // ou "admin" (réservé admin)
}
```
- **Réponse** :
```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "role": "user"
}
```

### b. Connexion (Login)
- **Endpoint** : `POST /api/auth/login/`
- **Payload** :
```json
{
  "username": "john",
  "password": "motdepasse"
}
```
- **Réponse** :
```json
{
  "refresh": "...",
  "access": "..."
}
```
- **À utiliser** :
  - Ajouter le header `Authorization: Bearer <access_token>` à toutes les requêtes protégées.

### c. Rafraîchir le token
- **Endpoint** : `POST /api/auth/refresh/`
- **Payload** :
```json
{
  "refresh": "..."
}
```
- **Réponse** :
```json
{
  "access": "..."
}
```

### d. Déconnexion (Blacklist du refresh token)
- **Endpoint** : `POST /api/auth/logout/`
- **Payload** :
```json
{
  "refresh": "..."
}
```

### e. Récupérer/modifier/supprimer un utilisateur (admin)
- **GET/PUT/PATCH** : `/api/users/<id>/update/` (admin)
- **DELETE** : `/api/users/<id>/delete/` (admin)
- **Réponse** :
```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "role": "user"
}
```

## 2. Gestion des rôles
- Le champ `role` dans la réponse utilisateur indique le rôle (`user`, `admin`, `public`).
- Le frontend doit adapter l'UI selon le rôle (ex : accès admin aux seuils d'alerte).

## 3. Alertes

### a. Lister les alertes actives
- **Endpoint** : `GET /api/alerts/`
- **Header** : `Authorization: Bearer <token>`
- **Réponse** :
```json
[
  {
    "id": 1,
    "type": "rain",
    "message": "Pluie détectée : 35 (seuil : 30)",
    "level": "warning",
    "status": "active",
    "created_at": "2024-06-01T12:00:00Z",
    "updated_at": "2024-06-01T12:00:00Z",
    "acknowledged_at": null,
    "resolved_at": null,
    "data": {"value": 35, "threshold": 30}
  }
]
```

### b. Historique des alertes
- **Endpoint** : `GET /api/alerts/history/`

### c. Accuser réception d'une alerte
- **Endpoint** : `PUT /api/alerts/<id>/acknowledge/`

### d. Résoudre une alerte
- **Endpoint** : `PUT /api/alerts/<id>/resolve/`

## 4. Seuils d'alerte (admin)

### a. Lister/créer/modifier/supprimer un seuil
- **Endpoint** : `/api/alert-thresholds/` (GET, POST, PUT, DELETE)
- **Payload création/modification** :
```json
{
  "type": "rain",
  "value": 30,
  "zone": "centre-ville"
}
```
- **Réponse** :
```json
{
  "id": 1,
  "type": "rain",
  "value": 30,
  "zone": "centre-ville"
}
```

## 5. Prédictions IA (admin)

### a. Lister/créer des prédictions
- **Endpoint** : `/api/predictions/` (GET, POST, PUT, DELETE)
- **Payload création** :
```json
{
  "type": "pollution",
  "value": 55.2,
  "date": "2024-06-02T12:00:00Z",
  "zone": "centre-ville"
}
```

### b. Déclencher l'analyse des prédictions (déclenchement d'alertes si dépassement)
- **Endpoint** : `POST /api/predictions/analyze/`
- **Réponse** :
```json
{
  "status": "Analyse terminée"
}
```

## 6. Gestion des erreurs
- **401 Unauthorized** : Token manquant ou invalide.
- **403 Forbidden** : Accès refusé (rôle insuffisant).
- **404 Not Found** : Ressource inexistante.
- **400 Bad Request** : Données invalides. 