from django.db import models
from .service_type import ServiceType

class Service(models.Model):
    
    CATEGORY_CHOICES = [
        ('I', 'Interior'),
        ('E', 'Exterior'),
        ('O', 'Other'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    # when a service is public it will be shown to customers and it will included in the create estimate view
    # we have many services that are not public and are only used for internal purposes like "taxes" or "fuel" "office cleaning", etc
    public = models.BooleanField(default=False)
    checklistActions = models.ManyToManyField('ChecklistAction', related_name='checklist_actions', blank=True)
    type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='type', blank=True, null=True)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='O')

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']