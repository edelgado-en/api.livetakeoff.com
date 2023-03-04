from django.db import models


class Tag(models.Model):
    COLOR_CHOICES = [
        ('red', 'red'),
        ('orange', 'orange'),
        ('amber', 'amber'),
        ('slate', 'slate'),
        ('lime', 'lime'),
        ('emerald', 'emerald'),
        ('cyan', 'cyan'),
        ('blue', 'blue'),
        ('indigo', 'indigo'),
        ('violet', 'violet'),
        ('fuchsia', 'fuchsia'),
        ('pink', 'pink'),
    ]

    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=255, blank=True, null=True, help_text='Short name for use in the UI (e.g. "LA" for "Late Arrival")')
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=255, choices=COLOR_CHOICES, default='red')

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']