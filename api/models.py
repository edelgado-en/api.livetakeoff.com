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
        ('W', 'WIP'),
        ('C', 'Complete'),
        ('T', 'Cancelled'),
        ('R', 'Review'),
        ('I', 'Invoiced'),

    ]
    #TODO: figure out how to do the purchase order number
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    requestDate = models.DateTimeField(auto_now_add=True)
    tailNumber = models.CharField(max_length=50)
    aircraftType = models.ForeignKey(AircraftType, on_delete=models.PROTECT)
    airport = models.ForeignKey(Airport, on_delete=models.PROTECT)
    fbo = models.ForeignKey(FBO, on_delete=models.PROTECT)
    estimatedETA = models.DateTimeField()
    estimatedETD = models.DateTimeField()
    completeBy = models.DateTimeField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    services = models.ManyToManyField(Service, related_name='services')
    retainerServices = models.ManyToManyField(RetainerService, related_name='retainerservices')
    assignees = models.ManyToManyField('auth.User', related_name='assignees')

    def __str__(self) -> str:
        return self.tailNumber + ' - ' + self.airport.initials + ' - ' + self.aircraftType.name

class JobComments(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    comment = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.comment

class JobPhotos(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    photourl = models.URLField()

    def __str__(self) -> str:
        return self.photo
    