from django.db import models

class TailIdent(models.Model):

    tail_number = models.CharField(max_length=255, unique=True)
    ident = models.CharField(max_length=255, unique=True)