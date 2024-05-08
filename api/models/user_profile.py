from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from .vendor import Vendor
from .customer import Customer

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='user_profiles', null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='user_profiles', null=True, blank=True)
    email_notifications = models.BooleanField(default=False)
    inventory_email_notifications = models.BooleanField(default=True, help_text='Only applicable to admins and account managers')
    sms_notifications = models.BooleanField(default=False)
    allow_set_as_busy = models.BooleanField(default=False)
    about = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    enable_estimates = models.BooleanField(default=False)
    enable_invoice = models.BooleanField(default=False)
    show_job_price = models.BooleanField(default=False)
    show_all_services_report = models.BooleanField(default=False,
                                                    help_text='If enabled, the external project manager will see all services completed by its vendor in the service report. If disabled, the external project manager will only see what its been completed by him/her')
    prompt_requested_by = models.BooleanField(default=False, help_text='For customers users that use generic profiles, this will prompt them to enter their name when creating a job.')

    show_airport_fees = models.BooleanField(default=False, help_text='If enabled, the user will be able to see airport and fbo additional fees when creating a job. The information will be shown when selecting an airport or fbo.')

    enable_confirm_jobs = models.BooleanField(default=False, help_text='If enabled, the user will be able to confirm jobs. If disabled, the user will not be able to confirm jobs. Admins can always confirm jobs.')

    enable_accept_jobs = models.BooleanField(default=False, help_text='If enabled, the user will be able to accept jobs. This is only applicable to project managers. If disabled, the project manager will skip the acceptance process and go straigh to start job.')

    enable_all_customers = models.BooleanField(default=False, help_text='If enabled, the user will be able to see all customers in the system. If disabled, the user will only see the customers that are associated with the user.')

    enable_all_airports = models.BooleanField(default=False, help_text='If enabled, the user will be able to see all airports in the system. If disabled, the user will only see the airports that are associated with the user.')

    ########################

    enable_email_notification_job_created = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is created.')

    enable_email_notification_scheduled_job_created = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a scheduled job is created.')

    enable_email_notification_job_completed = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is completed.')

    enable_email_notification_job_accepted = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is accepted.')

    enable_email_notification_job_confirmed = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is confirmed.')

    enable_email_notification_job_returned = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a job is returned.')

    enable_email_notification_job_comment_added = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when a comment is added to a job.')

    enable_email_notification_inventory_out_of_stock = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when an inventory item is out of stock.')

    enable_email_notification_inventory_threshold_met = models.BooleanField(default=False, help_text='If enabled, the user will receive an email notification when an inventory item reaches its threshold.')
    
    #####################

    enable_sms_notification_job_created = models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is created.')

    enable_sms_notification_job_completed = models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is completed.')

    enable_sms_notification_job_started = models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is started.')

    enable_sms_notification_job_cancelled = models.BooleanField(default=False, help_text='If enabled, the user will receive an sms notification when a job is cancelled.')








