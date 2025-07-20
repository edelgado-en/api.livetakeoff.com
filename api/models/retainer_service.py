from django.db import models

class RetainerService(models.Model):
    CATEGORY_CHOICES = [
        ('I', 'Interior'),
        ('E', 'Exterior'),
        ('O', 'Other'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    short_name = models.CharField(max_length=100, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    checklistActions = models.ManyToManyField('ChecklistAction', related_name='retainerchecklistActions')
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='O')
    is_special = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']