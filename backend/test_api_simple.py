#!/usr/bin/env python3
"""
Script de test simple pour l'API
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"

def test_api():
    print("🧪 Test de l'API Smart City")
    print("=" * 50)
    
    # Test 1: Connexion
    print("1. Test de connexion...")
    login_data = {
        "username": "tristan123",
        "password": "tristan123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"   ✅ Connexion réussie, token obtenu")
            
            # Test 2: Configuration de l'indice météo
            print("\n2. Test de la configuration de l'indice météo...")
            headers = {'Authorization': f'Bearer {token}'}
            
            config_response = requests.get(f"{BASE_URL}/api/weather-index/config/", headers=headers, timeout=10)
            print(f"   Status: {config_response.status_code}")
            
            if config_response.status_code == 200:
                config = config_response.json()
                print(f"   ✅ Configuration récupérée: {config}")
            else:
                print(f"   ❌ Erreur: {config_response.text}")
            
            # Test 3: Indice météo actuel
            print("\n3. Test de l'indice météo actuel...")
            current_response = requests.get(f"{BASE_URL}/api/weather-index/current/", headers=headers, timeout=10)
            print(f"   Status: {current_response.status_code}")
            
            if current_response.status_code == 200:
                current = current_response.json()
                print(f"   ✅ Indice actuel: {current}")
            else:
                print(f"   ❌ Erreur: {current_response.text}")
            
            # Test 4: Historique
            print("\n4. Test de l'historique...")
            history_response = requests.get(f"{BASE_URL}/api/weather-index/history/?page=1&page_size=5", headers=headers, timeout=10)
            print(f"   Status: {history_response.status_code}")
            
            if history_response.status_code == 200:
                history = history_response.json()
                print(f"   ✅ Historique récupéré: {len(history.get('results', []))} éléments")
            else:
                print(f"   ❌ Erreur: {history_response.text}")
            
            # Test 5: Alertes
            print("\n5. Test des alertes...")
            alerts_response = requests.get(f"{BASE_URL}/api/weather-index/alerts/?status=active", headers=headers, timeout=10)
            print(f"   Status: {alerts_response.status_code}")
            
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                print(f"   ✅ Alertes récupérées: {len(alerts)} alertes actives")
            else:
                print(f"   ❌ Erreur: {alerts_response.text}")
                
        else:
            print(f"   ❌ Erreur de connexion: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Impossible de se connecter au serveur")
    except requests.exceptions.Timeout:
        print("   ❌ Timeout de la requête")
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")

if __name__ == "__main__":
    test_api() 