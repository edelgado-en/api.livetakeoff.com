from django.db.models import Q
from api.notification_util import NotificationUtil

from django.contrib.auth.models import User

from api.models import (
    UserProfile,
    Job,
    JobServiceAssignment,
    JobRetainerServiceAssignment,
    JobEstimate,
    UserCustomer
)

class SMSNotificationService():
    
    def send_create_job_notification(self, job: Job, current_user: User):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    sms_notifications=True,
                                                    enable_sms_notification_job_created=True,
                                                    phone_number__isnull=False,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))
        
        customer_users = UserProfile.objects.filter(user__is_active=True,
                                                    customer=job.customer,
                                                    sms_notifications=True,
                                                    phone_number__isnull=False,
                                                    enable_sms_notification_job_created=True,
                                                    enable_confirm_jobs=True).exclude(user=current_user)
        
        unique_phone_numbers = []

        for user_profile in internal_users:
            if user_profile.user.groups.filter(name='Internal Coordinators').exists():
                if user_profile.enable_all_customers:
                    if user_profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user_profile.phone_number)
                
                else:
                    user_customers = UserCustomer.objects.filter(user=user_profile.user, customer_id=job.customer.id)
                    if user_customers:
                        if user_profile.phone_number not in unique_phone_numbers:
                            unique_phone_numbers.append(user_profile.phone_number)
            
            else:
                if user_profile.phone_number not in unique_phone_numbers:
                    unique_phone_numbers.append(user_profile.phone_number)

        for user_profile in customer_users:
            if user_profile.phone_number not in unique_phone_numbers:
                unique_phone_numbers.append(user_profile.phone_number)

        etd = 'Not Specified'
        if job.estimatedETD:
            etd = job.estimatedETD.strftime('%m/%d/%y %H:%M')

        eta = 'Not Specified'
        if job.estimatedETA:
            eta = job.estimatedETA.strftime('%m/%d/%y %H:%M')

        notification_util = NotificationUtil()
        message = f'JOB SUBMITTED\n•⁠  ⁠{job.customer.name}\n•⁠  ⁠{job.airport.initials}\n•⁠  ⁠{job.tailNumber}\nETA: {eta}\nETD: {etd}'

        for phone_number in unique_phone_numbers:
            notification_util.send(message, phone_number.as_e164)


    def send_job_assigned_notification(self, job: Job, unique_phone_numbers: list):
        message = f'Job ASSIGNED to you\n• {job.airport.initials}\n• {job.tailNumber}\n• {job.fbo.name}\n'

        notification_util = NotificationUtil()

        for phone_number in unique_phone_numbers:
            notification_util.send(message, phone_number.as_e164)


    def send_job_completed_notification(self, job: Job):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    sms_notifications=True,
                                                    enable_sms_notification_job_completed=True,
                                                    phone_number__isnull=False,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))
        unique_phone_numbers = []

        for user_profile in internal_users:
            if user_profile.user.groups.filter(name='Internal Coordinators').exists():
                if user_profile.enable_all_customers:
                    if user_profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user_profile.phone_number)
                
                else:
                    user_customers = UserCustomer.objects.filter(user=user_profile.user, customer_id=job.customer.id)
                    if user_customers:
                        if user_profile.phone_number not in unique_phone_numbers:
                            unique_phone_numbers.append(user_profile.phone_number)
            
            else:
                if user_profile.phone_number not in unique_phone_numbers:
                    unique_phone_numbers.append(user_profile.phone_number)

        # Notify the user that created the job
        user_profile = job.created_by.profile

        if user_profile.customer \
            and user_profile.sms_notifications \
            and user_profile.enable_sms_notification_job_completed \
            and user_profile.phone_number:
            if user_profile.phone_number not in unique_phone_numbers:
                unique_phone_numbers.append(user_profile.phone_number)

        notification_util = NotificationUtil()
        message = f'JOB COMPLETED\n•⁠  ⁠{job.customer.name}\n•⁠  ⁠{job.airport.initials}\n•⁠  ⁠{job.tailNumber}'

        for phone_number in unique_phone_numbers:
            notification_util.send(message, phone_number.as_e164)


    def send_job_started_notification(self, job: Job, first_name: str):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    sms_notifications=True,
                                                    enable_sms_notification_job_started=True,
                                                    phone_number__isnull=False,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))
        notification_util = NotificationUtil()

        message = f'Job STARTED by {first_name}\n• {job.customer.name}\n• {job.airport.initials}\n• {job.tailNumber}\n'

        unique_phone_numbers = []

        for user_profile in internal_users:
            if user_profile.user.groups.filter(name='Internal Coordinators').exists():
                if user_profile.enable_all_customers:
                    if user_profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user_profile.phone_number)
                
                else:
                    user_customers = UserCustomer.objects.filter(user=user_profile.user, customer_id=job.customer.id)
                    if user_customers:
                        if user_profile.phone_number not in unique_phone_numbers:
                            unique_phone_numbers.append(user_profile.phone_number)
            
            else:
                if user_profile.phone_number not in unique_phone_numbers:
                    unique_phone_numbers.append(user_profile.phone_number)

        # Notify the user that created the job
        user_profile = job.created_by.profile

        if user_profile.customer \
            and user_profile.sms_notifications \
            and user_profile.enable_sms_notification_job_started \
            and user_profile.phone_number:
            if user_profile.phone_number not in unique_phone_numbers:
                unique_phone_numbers.append(user_profile.phone_number)

        for phone_number in unique_phone_numbers:
            notification_util.send(message, phone_number.as_e164)


    def send_job_cancelled_notification(self, job: Job, first_name: str):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    sms_notifications=True,
                                                    enable_sms_notification_job_cancelled=True,
                                                    phone_number__isnull=False,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))
        notification_util = NotificationUtil()

        message = f'Job CANCELLED by {first_name}\n• {job.customer.name}\n• {job.airport.initials}\n• {job.tailNumber}\n'

        unique_phone_numbers = []

        for user_profile in internal_users:
            if user_profile.user.groups.filter(name='Internal Coordinators').exists():
                if user_profile.enable_all_customers:
                    if user_profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user_profile.phone_number)
                
                else:
                    user_customers = UserCustomer.objects.filter(user=user_profile.user, customer_id=job.customer.id)
                    if user_customers:
                        if user_profile.phone_number not in unique_phone_numbers:
                            unique_phone_numbers.append(user_profile.phone_number)
            
            else:
                if user_profile.phone_number not in unique_phone_numbers:
                    unique_phone_numbers.append(user_profile.phone_number)

        for phone_number in unique_phone_numbers:
            notification_util.send(message, phone_number.as_e164)


    def send_job_comment_added_notification(self, job: Job):
        # get all phone numbers for all project managers assigned to this job
        unique_phone_numbers = []
        
        job_service_assignments = JobServiceAssignment.objects \
                                                        .select_related('project_manager').filter(job=job)
        
        for assignment in job_service_assignments:
            user = assignment.project_manager
            
            if user and user.profile.phone_number:
                if user.profile.phone_number not in unique_phone_numbers:
                    unique_phone_numbers.append(user.profile.phone_number)

        job_retainer_service_assignments = JobRetainerServiceAssignment.objects \
                                                        .select_related('project_manager').filter(job=job)
        
        for assignment in job_retainer_service_assignments:
            user = assignment.project_manager
            
            if user and user.profile.phone_number:
                if user.profile.phone_number not in unique_phone_numbers:
                    unique_phone_numbers.append(user.profile.phone_number)

        notification_util = NotificationUtil()

        message = 'Important note was added to this job'
        message += f'\n• {job.airport.initials}\n• {job.tailNumber}\n• {job.fbo.name}\n'

        for phone_number in unique_phone_numbers:
            notification_util.send(message, phone_number.as_e164)


    def send_job_estimate_notification(self, job_estimate: JobEstimate):
        phone_number = job_estimate.requested_by.profile.phone_number

        if phone_number is None:
            return

        status_name = 'REJECTED'

        if job_estimate.status == 'A':
            status_name = 'ACCEPTED'

        message = f'Estimate {status_name} for {job_estimate.tailNumber} at {job_estimate.airport.initials}.'
        
        notification_util = NotificationUtil()

        notification_util.send(message, phone_number.as_e164)
    