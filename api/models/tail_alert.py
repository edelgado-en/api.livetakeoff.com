from django.db import models

class TailAlert(models.Model):
    tailNumber = models.CharField(max_length=50, unique=True)
    message = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
