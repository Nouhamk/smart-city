#!/usr/bin/env python3
"""
Script de test pour vérifier les endpoints de l'indice météo
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
WEATHER_INDEX_URL = f"{BASE_URL}/api/weather-index"

def test_login():
    """Test de connexion pour obtenir un token"""
    print("🔐 Test de connexion...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"✅ Connexion réussie, token obtenu")
            return token
        else:
            print(f"❌ Échec de connexion: {response.status_code}")
            print(f"Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def test_endpoint(url, token, name):
    """Test d'un endpoint spécifique"""
    print(f"\n🔍 Test de {name}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name} fonctionne")
            print(f"Données reçues: {json.dumps(data, indent=2, default=str)[:200]}...")
            return True
        else:
            print(f"❌ {name} échoue")
            print(f"Erreur: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test de {name}: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test des endpoints de l'indice météo")
    print("=" * 50)
    
    # Test de connexion
    token = test_login()
    if not token:
        print("❌ Impossible de continuer sans token")
        return
    
    # Tests des endpoints
    endpoints = [
        (f"{WEATHER_INDEX_URL}/current/", "Indice météo actuel"),
        (f"{WEATHER_INDEX_URL}/config/", "Configuration"),
        (f"{WEATHER_INDEX_URL}/history/?page=1&page_size=5", "Historique"),
        (f"{WEATHER_INDEX_URL}/alerts/?status=active", "Alertes actives"),
    ]
    
    results = []
    for url, name in endpoints:
        result = test_endpoint(url, token, name)
        results.append((name, result))
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Résultat: {success_count}/{total_count} endpoints fonctionnent")
    
    if success_count == total_count:
        print("🎉 Tous les endpoints fonctionnent correctement !")
    else:
        print("⚠️  Certains endpoints ont des problèmes")

if __name__ == "__main__":
    main() 