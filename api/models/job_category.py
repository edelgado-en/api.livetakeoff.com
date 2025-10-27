from django.db import models
from .job import Job
from .customer_category import CustomerCategory

class JobCategory(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='categories')
    customer_category = models.ForeignKey(CustomerCategory, on_delete=models.CASCADE, related_name='job_categories')
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT, related_name='job_categories', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self) -> str:
        return f'Job ID: {self.job.id} - Category: {self.customer_category.name}'

    class Meta:
        verbose_name_plural = 'Job Categories'