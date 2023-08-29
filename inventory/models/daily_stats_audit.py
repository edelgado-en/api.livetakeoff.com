from django.db import models

class DailyStatsAudit(models.Model):
    last_updated = models.DateField()