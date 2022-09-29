from django.db import models
from django.utils.html import mark_safe

class Service(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    checklistActions = models.ManyToManyField('ChecklistAction', related_name='checklistActions')

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']

class RetainerService(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    checklistActions = models.ManyToManyField('ChecklistAction', related_name='retainerchecklistActions')

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']

class ChecklistAction(models.Model):
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']

class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    billingAddress = models.TextField(blank=True, null=True)
    emailAddress = models.EmailField(blank=True, null=True, unique=True)
    #TODO: logo is an image. We can save this in the database
    billingInfo = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

class AircraftType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']

class Airport(models.Model):
    initials = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['initials']

class FBO(models.Model):
    name = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']

class Job(models.Model):
    STATUS_CHOICES = [
        ('A', 'Accepted'),
        ('S', 'Assigned'),
        ('U', 'Submitted'),
        ('W', 'WIP'),
        ('C', 'Complete'),
        ('T', 'Cancelled'),
        ('R', 'Review'),
        ('I', 'Invoiced'),

    ]
    #TODO: figure out how to do the purchase order number
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='jobs')
    requestDate = models.DateTimeField(auto_now_add=True)
    tailNumber = models.CharField(max_length=50)
    aircraftType = models.ForeignKey(AircraftType, on_delete=models.PROTECT)
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT)
    fbo = models.ForeignKey(FBO, on_delete=models.PROTECT)
    estimatedETA = models.DateTimeField(blank=True, null=True)
    estimatedETD = models.DateTimeField(blank=True, null=True)
    completeBy = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    services = models.ManyToManyField(Service, related_name='services', blank=True)
    retainerServices = models.ManyToManyField(RetainerService, related_name='retainerservices', blank=True)
    assignees = models.ManyToManyField('auth.User', related_name='assignees', blank=True)

    def __str__(self) -> str:
        return str(self.id) + ' - ' + self.tailNumber + ' - ' + self.airport.initials + ' - ' + self.aircraftType.name

class JobComments(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.comment

class JobPhotos(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='photos')
    name = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to='images/', blank=True)
    interior = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    @property
    def image_preview(self):
        if self.image:
            return mark_safe('<img src="{}" width="300" height="300" />'.format(self.image.url))
        return ""
    
    class Meta:
        verbose_name_plural = 'Job Photos'
    