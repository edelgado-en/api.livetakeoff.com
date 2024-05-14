from django.db import models

class Airport(models.Model):
    initials = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=255, unique=True)
    # when a airport is public it will be shown to customers and it will included in the create estimate view
    public = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    preferred_project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='preferred_airports', null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['initials']