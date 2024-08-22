from django.db import models

class FBO(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # when a fbo is public it will be shown to customers and it will included in the create estimate view
    public = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    hours_of_operation = models.CharField(max_length=255, blank=True, null=True)
    fee = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    fee_percentage = models.BooleanField(default=False, help_text='If true, the fee is of type percentage, otherwise it is a fixed fee.')

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']