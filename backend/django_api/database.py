from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# User functions
def create_user(username: str, email: str, password: str, role: str = 'user') -> Dict[str, Any]:
    """Create a new user in Supabase"""
    user_data = {
        'username': username,
        'email': email,
        'password': password,  # In production, hash this!
        'role': role,
        'created_at': datetime.now().isoformat()
    }

    response = supabase.table("custom_user").insert(user_data).execute()
    return response.data[0] if response.data else None

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username"""
    response = supabase.table("custom_user").select("*").eq("username", username).execute()
    return response.data[0] if response.data else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    response = supabase.table("custom_user").select("*").eq("id", user_id).execute()
    return response.data[0] if response.data else None

def update_user(user_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update user data"""
    response = supabase.table("custom_user").update(data).eq("id", user_id).execute()
    return response.data[0] if response.data else None

def delete_user(user_id: int) -> bool:
    """Delete user"""
    response = supabase.table("custom_user").delete().eq("id", user_id).execute()
    return len(response.data) > 0

# Alert functions
def create_alert(alert_type: str, message: str, level: str = 'warning', data: Dict = None) -> Dict[str, Any]:
    """Create a new alert"""
    alert_data = {
        'type': alert_type,
        'message': message,
        'level': level,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'data': data
    }

    response = supabase.table("alert").insert(alert_data).execute()
    return response.data[0] if response.data else None

def get_active_alerts() -> List[Dict[str, Any]]:
    """Get all active alerts"""
    response = supabase.table("alert").select("*").eq("status", "active").execute()
    return response.data

def get_alert_history() -> List[Dict[str, Any]]:
    """Get non-active alerts"""
    response = supabase.table("alert").select("*").neq("status", "active").execute()
    return response.data

def acknowledge_alert(alert_id: int) -> Optional[Dict[str, Any]]:
    """Acknowledge an alert"""
    update_data = {
        'status': 'acknowledged',
        'acknowledged_at': datetime.now().isoformat()
    }
    response = supabase.table("alert").update(update_data).eq("id", alert_id).execute()
    return response.data[0] if response.data else None

def resolve_alert(alert_id: int) -> Optional[Dict[str, Any]]:
    """Resolve an alert"""
    update_data = {
        'status': 'resolved',
        'resolved_at': datetime.now().isoformat()
    }
    response = supabase.table("alert").update(update_data).eq("id", alert_id).execute()
    return response.data[0] if response.data else None

def get_alert_by_id(alert_id: int) -> Optional[Dict[str, Any]]:
    """Get alert by ID"""
    response = supabase.table("alert").select("*").eq("id", alert_id).execute()
    return response.data[0] if response.data else None

# Alert Threshold functions
def create_alert_threshold(threshold_type: str, value: float, zone: str = None) -> Dict[str, Any]:
    """Create alert threshold"""
    threshold_data = {
        'type': threshold_type,
        'value': value,
        'zone': zone
    }

    response = supabase.table("alert_threshold").insert(threshold_data).execute()
    return response.data[0] if response.data else None

def get_alert_thresholds() -> List[Dict[str, Any]]:
    """Get all alert thresholds"""
    response = supabase.table("alert_threshold").select("*").execute()
    return response.data

def get_alert_threshold(threshold_type: str, zone: str = None) -> Optional[Dict[str, Any]]:
    """Get specific alert threshold"""
    query = supabase.table("alert_threshold").select("*").eq("type", threshold_type)
    if zone:
        query = query.eq("zone", zone)
    else:
        query = query.is_("zone", "null")

    response = query.execute()
    return response.data[0] if response.data else None

def update_alert_threshold(threshold_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update alert threshold"""
    response = supabase.table("alert_threshold").update(data).eq("id", threshold_id).execute()
    return response.data[0] if response.data else None

def delete_alert_threshold(threshold_id: int) -> bool:
    """Delete alert threshold"""
    response = supabase.table("alert_threshold").delete().eq("id", threshold_id).execute()
    return len(response.data) > 0

# Prediction functions
def create_prediction(pred_type: str, value: float, date: str, zone: str = None) -> Dict[str, Any]:
    """Create prediction"""
    prediction_data = {
        'type': pred_type,
        'value': value,
        'date': date,
        'zone': zone,
        'created_at': datetime.now().isoformat()
    }

    response = supabase.table("prediction").insert(prediction_data).execute()
    return response.data[0] if response.data else None

def get_predictions() -> List[Dict[str, Any]]:
    """Get all predictions"""
    response = supabase.table("prediction").select("*").execute()
    return response.data

def get_prediction_by_id(prediction_id: int) -> Optional[Dict[str, Any]]:
    """Get prediction by ID"""
    response = supabase.table("prediction").select("*").eq("id", prediction_id).execute()
    return response.data[0] if response.data else None

def update_prediction(prediction_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update prediction"""
    response = supabase.table("prediction").update(data).eq("id", prediction_id).execute()
    return response.data[0] if response.data else None

def delete_prediction(prediction_id: int) -> bool:
    """Delete prediction"""
    response = supabase.table("prediction").delete().eq("id", prediction_id).execute()
    return len(response.data) > 0

def analyze_predictions() -> str:
    """Analyze predictions and create alerts"""
    predictions = get_predictions()

    for pred in predictions:
        threshold_data = get_alert_threshold(pred['type'], pred.get('zone'))
        if not threshold_data:
            continue

        if pred['value'] > threshold_data['value']:
            create_alert(
                alert_type=pred['type'],
                message=f"Prédiction : {pred['value']} dépasse le seuil {threshold_data['value']}",
                level='warning',
                data={
                    'prediction_id': pred['id'],
                    'value': pred['value'],
                    'threshold': threshold_data['value']
                }
            )

    return 'Analyse terminée'

# Region functions
def get_regions() -> List[Dict[str, Any]]:
    """Get all regions"""
    response = supabase.table("region").select("*").execute()
    return response.data