from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class CustomUser(AbstractUser):
    phoneNumber = models.CharField(max_length=15, blank=True, null=True)
    ProfilePictures = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} {self.email}"



class UserSymptoms(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='symptoms')
    symptoms = models.TextField()  # Storing symptoms in a text field
    created_at = models.DateTimeField(auto_now_add=True)
    symptoms_severity = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.symptoms[:20]}'


class AnalysisResults(models.Model):
    user_symptom = models.OneToOneField(UserSymptoms, on_delete=models.CASCADE)
    results = models.TextField()  # Storing analysis results
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Analysis for {self.user_symptom}'

class DailyCheckup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_checkups')
    checkup_date = models.DateField()
    checkup_data = models.TextField()  # Stores health info
    suggestions = models.TextField()  # Stores daily suggestions
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.checkup_date}'
    
# models.py
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message[:20]}'