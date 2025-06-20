from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('public', 'Public'),
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user') 

class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('rain', 'Pluie'),
        ('heatwave', 'Vague de chaleur'),
        ('wind', 'Vent fort'),
        ('custom', 'Personnalisée'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Reconnue'),
        ('resolved', 'Résolue'),
        ('archived', 'Archivée'),
    ]
    type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    message = models.TextField()
    level = models.CharField(max_length=20, default='warning')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.type} - {self.status} - {self.created_at}" 

class AlertThreshold(models.Model):
    type = models.CharField(max_length=20)  # ex: 'rain', 'heatwave', 'pollution', etc.
    value = models.FloatField()
    zone = models.CharField(max_length=50, blank=True, null=True)  # optionnel, pour la gestion par zone

    def __str__(self):
        return f"{self.type} - {self.value} - {self.zone or 'global'}"

class Prediction(models.Model):
    type = models.CharField(max_length=20)  # ex: 'pollution', 'rain', etc.
    value = models.FloatField()
    date = models.DateTimeField()
    zone = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.value} - {self.date} - {self.zone or 'global'}" 