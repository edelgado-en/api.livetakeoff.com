from django.db import models

class Airport(models.Model):
    
    TYPE_CHOICES = [
        ('E', 'External'),
        ('I', 'Internal'),
        ('B', 'Both'),
    ]
    
    initials = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=255, unique=True)
    # when a airport is public it will be shown to customers and it will included in the create estimate view
    public = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    preferred_project_manager = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='preferred_airports', null=True, blank=True)
    airport_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='E')
    fee = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    fee_percentage = models.BooleanField(default=False, help_text='If true, the fee is of type percentage, otherwise it is a fixed fee.')

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['initials']