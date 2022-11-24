from django.db import models

class FBO(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # when a fbo is public it will be shown to customers and it will included in the create estimate view
    public = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']