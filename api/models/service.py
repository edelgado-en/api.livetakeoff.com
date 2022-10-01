from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    checklistActions = models.ManyToManyField('ChecklistAction', related_name='checklistActions')

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']