from django.db import models
from .brand import Brand

class Item(models.Model):

    measure_by_choices = (
        ('U', 'Unit'),
        ('G', 'Gallons'),
        ('B', 'Bottle'),
        ('O', 'Box'),
        ('L', 'Lb'),
        ('J', 'Jar'),
        ('T', 'Other')
    )

    area_choices = (
        ('I', 'Interior'),
        ('E', 'Exterior'),
        ('B', 'Interior and Exterior'),
        ('O', 'Office'),
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='items')
    measure_by = models.CharField(max_length=1, choices=measure_by_choices, default='U')
    area = models.CharField(max_length=1, choices=area_choices, default='I')
    cost_per_unit = models.DecimalField(max_digits=9, decimal_places=2)
    photo = models.ImageField(upload_to='images/', blank=True)
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='items')

    def __str__(self) -> str:
        return self.name

