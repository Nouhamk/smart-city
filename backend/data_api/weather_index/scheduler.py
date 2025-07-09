from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from .weather_index_calculator import weather_index_calculator
from .alert_service import weather_index_alert_service

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherIndexScheduler:
    """
    Planificateur pour le calcul automatique de l'indice météo
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """
        Démarre le planificateur
        """
        if not self.is_running:
            # Tâche toutes les heures (minute 0 de chaque heure)
            self.scheduler.add_job(
                func=self._calculate_and_check_alerts,
                trigger=CronTrigger(minute=0),
                id='weather_index_calculation',
                name='Calcul de l\'indice météo global',
                replace_existing=True
            )
            
            # Tâche de démarrage immédiat
            self.scheduler.add_job(
                func=self._calculate_and_check_alerts,
                trigger='date',
                id='weather_index_initial',
                name='Calcul initial de l\'indice météo'
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Planificateur d'indice météo démarré")
    
    def stop(self):
        """
        Arrête le planificateur
        """
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Planificateur d'indice météo arrêté")
    
    def _calculate_and_check_alerts(self):
        """
        Calcule l'indice météo et vérifie les alertes
        """
        try:
            logger.info(f"Début du calcul de l'indice météo - {datetime.now()}")
            
            # Calculer l'indice météo pour toutes les régions
            weather_indices = weather_index_calculator.get_latest_weather_index()
            
            logger.info(f"Indices calculés pour {len(weather_indices)} régions")
            
            # Vérifier et créer les alertes
            alerts_created = weather_index_alert_service.check_and_create_alerts()
            
            if alerts_created:
                logger.info(f"{len(alerts_created)} alertes créées/mises à jour")
                for alert in alerts_created:
                    logger.info(f"Alerte {alert['action']} pour {alert['region']} - Niveau: {alert['level']}")
            else:
                logger.info("Aucune nouvelle alerte créée")
            
            logger.info(f"Calcul de l'indice météo terminé - {datetime.now()}")
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul de l'indice météo: {e}")
    
    def get_scheduler_status(self):
        """
        Retourne le statut du planificateur
        """
        if not self.is_running:
            return {'status': 'stopped'}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'status': 'running',
            'jobs': jobs
        }

# Instance globale du planificateur
weather_index_scheduler = WeatherIndexScheduler() 