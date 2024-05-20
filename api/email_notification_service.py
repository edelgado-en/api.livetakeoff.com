import base64
from django.db.models import Q
from api.email_util import EmailUtil
import time

from django.contrib.auth.models import User

from api.models import (
    UserProfile,
    UserEmail,
    Job,
    Service,
    RetainerService,
    JobSchedule,
    UserCustomer,
    LastProjectManagersNotified,
    JobAcceptanceNotification
)

class EmailNotificationService():
    
    def send_create_job_notification(self, job: Job,
                                     services: [Service],
                                     retainer_services: [RetainerService],
                                     current_user: User):
        
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_job_created=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))
        
        unique_emails = self.get_unique_emails(internal_users, job.customer.id)
        
        if job.customer.customer_settings.enable_approval_process:
            current_user_enable_confirm_jobs = current_user.profile.enable_confirm_jobs

            if not current_user_enable_confirm_jobs:
                customer_users = UserProfile.objects.filter(user__is_active=True,
                                                            customer=job.customer,
                                                            email_notifications=True,
                                                            enable_email_notification_job_created=True,
                                                            enable_confirm_jobs=True).exclude(user=current_user)
                
                for user_profile in customer_users:
                    if user_profile.user.email and user_profile.user.email not in unique_emails:
                        unique_emails.append(user_profile.user.email)

                    additional_emails = UserEmail.objects.filter(user=user_profile.user)
                    for additional_email in additional_emails:
                        if additional_email.email not in unique_emails:
                            unique_emails.append(additional_email.email)


        email_util = EmailUtil()
        subject = f'{job.tailNumber} - Job SUBMITTED by {job.customer.name}'
        body = self.build_email_body_for_job_creation(job, services, retainer_services, email_util)

        for email in unique_emails:
            email_util.send_email(email, subject, body)


    def send_job_completed_notification(self, job: Job, user: User):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_job_completed=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))
        
        unique_emails = self.get_unique_emails(internal_users, job.customer.id)

        # Notify the user that created the job
        user_profile = job.created_by.profile

        if user_profile.customer \
            and user_profile.email_notifications \
            and user_profile.enable_email_notification_job_completed:
            if user_profile.user.email and user_profile.user.email not in unique_emails:
                unique_emails.append(user_profile.user.email)
            
            additional_emails = UserEmail.objects.filter(user=user_profile.user)
            for additional_email in additional_emails:
                if additional_email.email not in unique_emails:
                    unique_emails.append(additional_email.email)

        email_util = EmailUtil()

        full_name = user.first_name + ' ' + user.last_name
        
        subject = f'{job.tailNumber} - Job COMPLETED'
        body = self.build_email_body(job, 'Job Completed', '', email_util)

        for email in unique_emails:
            email_util.send_email(email, subject, body)


    def send_job_accepted_notification(self, job: Job, full_name: str):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_job_accepted=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))

        unique_emails = self.get_unique_emails(internal_users, job.customer.id)

        email_util = EmailUtil()

        subject = f'{job.tailNumber} - Job ACCEPTED by {full_name}'
        body = self.build_email_body(job, 'Job Accepted', '', email_util)

        for email in unique_emails:
            email_util.send_email(email, subject, body)


    def send_job_comment_added_notification(self, job: Job, comment: str, emails: [str]):
        email_util = EmailUtil()

        subject = f'{job.tailNumber} Job Comment Added'
        body = self.build_email_body(job, 'Job Comment Added', comment, email_util)

        for email_address in emails:
            email_util.send_email(email_address, subject, body)


    def send_job_comment_added_notification_to_admins(self, job: Job,
                                            comment: str,
                                            is_customer_user: bool,
                                            is_external_project_manager: bool):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_job_comment_added=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))

        unique_emails = self.get_unique_emails(internal_users, job.customer.id)

        email_util = EmailUtil()
        
        subject = ''
        if is_customer_user:
            subject = f'{job.tailNumber} - CUSTOMER ADDED COMMENT'
        elif is_external_project_manager:
            subject = f'{job.tailNumber} - EXTERNAL PROJECT MANAGER ADDED COMMENT'

        body = self.build_email_body(job, 'Job Comment Added', comment, email_util)

        for email in unique_emails:
            email_util.send_email(email, subject, body)


    def send_job_confirmed_notification(self, job: Job, full_name: str):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_job_confirmed=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))

        unique_emails = self.get_unique_emails(internal_users, job.customer.id)

        email_util = EmailUtil()

        subject = f'{job.tailNumber} - Job CONFIRMED by {full_name}'
        body = self.build_email_body(job, 'Job Confirmed', '', email_util)

        for email in unique_emails:
            email_util.send_email(email, subject, body)

    
    def send_job_returned_notification(self, job: Job, full_name: str, comment: str):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_job_returned=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))

        unique_emails = self.get_unique_emails(internal_users, job.customer.id)

        email_util = EmailUtil()

        subject = f'{job.tailNumber} - Job RETURNED by {full_name}'
        body = self.build_email_body(job, 'Job Returned', comment, email_util)

        for email in unique_emails:
            email_util.send_email(email, subject, body)
            

    def send_inventory_out_of_stock_notification(self, location_item):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_inventory_out_of_stock=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))

        unique_emails = self.get_unique_emails(internal_users)

        subject = f'OUT OF STOCK {location_item.item.name} at {location_item.location.name}'

        body = f'''
        <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">OUT OF STOCK Item Notification</div>
        
        <div>
            <div style="padding:5px;font-weight: 700;">Item</div>
            <div style="padding:5px">{location_item.item.name}</div>
            <div style="padding:5px;font-weight: 700;">Location</div>
            <div style="padding:5px">{location_item.location.name}</div>
            <div style="padding:5px;font-weight: 700;">Quantity</div>
            <div style="padding:5px">OUT OF STOCK</div>
        </div>
        '''

        email_util = EmailUtil()

        body += email_util.getEmailSignature()

        for email in unique_emails:
            email_util.send_email(email, subject, body)


    def send_inventory_threshold_met_notification(self, location_item):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_inventory_threshold_met=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))

        unique_emails = self.get_unique_emails(internal_users)

        subject = f'THRESHOLD MET {location_item.item.name} at {location_item.location.name}'

        body = f'''
        <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">THRESHOLD Item Notification</div>
        
        <div>
            <div style="padding:5px;font-weight: 700;">Item</div>
            <div style="padding:5px">{location_item.item.name}</div>
            <div style="padding:5px;font-weight: 700;">Location</div>
            <div style="padding:5px">{location_item.location.name}</div>
            <div style="padding:5px;font-weight: 700;">Quantity</div>
            <div style="padding:5px">{location_item.quantity}</div>
            <div style="padding:5px;font-weight: 700;">Threshold</div>
            <div style="padding:5px">{location_item.threshold}</div>
        </div>
        '''

        email_util = EmailUtil()

        body += email_util.getEmailSignature()

        for email in unique_emails:
            email_util.send_email(email, subject, body)

    
    def send_scheduled_job_created_notification(self, job_schedule: JobSchedule):
        internal_users = UserProfile.objects.filter(user__is_active=True,
                                                    email_notifications=True,
                                                    enable_email_notification_scheduled_job_created=True,
                                                    user__in=User.objects.filter(Q(is_superuser=True)
                                                                         | Q(is_staff=True)
                                                                         | Q(groups__name='Account Managers')
                                                                         | Q(groups__name='Internal Coordinators')))
        
        unique_emails = self.get_unique_emails(internal_users, job_schedule.customer.id)

        subject = f'Scheduled Job Created - {job_schedule.customer.name} - {job_schedule.tailNumber}'

        body = f'''
                <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Scheduled Job</div>
                <table style="border-collapse: collapse">
                    <tr>
                        <td style="padding:15px">Customer</td>
                        <td style="padding:15px">{job_schedule.customer.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Tail</td>
                        <td style="padding:15px">{job_schedule.tailNumber}</td>
                    </tr>
                </table>
                
                '''
        email_util = EmailUtil()
        
        body += email_util.getEmailSignature()

        for email in unique_emails:
            email_util.send_email(email, subject, body)


    def send_job_assigned_notification(self, job: Job, emails: [str],
                                    service_names: str, retainer_service_names: str):
        email_util = EmailUtil()

        subject = f'{job.tailNumber} - Job ASSIGNED - Review and ACCEPT it or RETURN it as soon as possible.'
        
        message = str(job.id) + '-' + job.tailNumber
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        body = f'''
                <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Job Assignment</div>
                <a href="http://livetakeoff.com/shared/jobs/{base64_message}/accept" style="display: inline-block; padding: 0.5625rem 1.125rem; margin: 0 5px; font-size: 1.5rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.375rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #fff; background-color: #007bff; border-color: #007bff;">ACCEPT</a>
                <a href="http://livetakeoff.com/shared/jobs/{base64_message}/accept" style="display: inline-block; padding: 0.5625rem 1.125rem; margin: 0 5px; font-size: 1.5rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.375rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #212529; background-color: #f8f9fa; border-color: #f8f9fa;">RETURN</a>

                <div style="margin-bottom:20px"></div>
                <table style="border-collapse: collapse">
                    <tr>
                        <td style="padding:15px">Job PO</td>
                        <td style="padding:15px">{job.purchase_order}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Tail</td>
                        <td style="padding:15px">{job.tailNumber}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Airport</td>
                        <td style="padding:15px">{job.airport.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">FBO</td>
                        <td style="padding:15px">{job.fbo.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Arrival</td>
                        <td style="padding:15px">{job.arrival_formatted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Departure</td>
                        <td style="padding:15px">{job.departure_formatted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Complete Before</td>
                        <td style="padding:15px">{job.complete_before_formatted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Services</td>
                        <td style="padding:15px">{service_names}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Retainer Services</td>
                        <td style="padding:15px">{retainer_service_names}</td>
                    </tr>
                </table>
                <div style="margin-top:20px;padding:5px;font-weight: 700;"></div>
                '''

        email_util = EmailUtil()

        body += email_util.getEmailSignature()

        for email_address in emails:
            email_util.send_email(email_address, subject, body)



    def get_unique_emails(self, user_profiles: [UserProfile], customer_id: int = None):
        unique_emails = []

        for user_profile in user_profiles:
            if user_profile.user.groups.filter(name='Internal Coordinators').exists():
                if user_profile.enable_all_customers:
                    if user_profile.user.email and user_profile.user.email not in unique_emails:
                        unique_emails.append(user_profile.user.email)

                    additional_emails = UserEmail.objects.filter(user=user_profile.user)
                    for additional_email in additional_emails:
                        if additional_email.email not in unique_emails:
                            unique_emails.append(additional_email.email)

                else:
                    if customer_id:
                        user_customers = UserCustomer.objects.filter(user=user_profile.user, customer_id=customer_id)
                        if user_customers:
                            if user_profile.user.email and user_profile.user.email not in unique_emails:
                                unique_emails.append(user_profile.user.email)

                            additional_emails = UserEmail.objects.filter(user=user_profile.user)
                            for additional_email in additional_emails:
                                if additional_email.email not in unique_emails:
                                    unique_emails.append(additional_email.email)

            else:
                if user_profile.user.email and user_profile.user.email not in unique_emails:
                    unique_emails.append(user_profile.user.email)

                additional_emails = UserEmail.objects.filter(user=user_profile.user)
                for additional_email in additional_emails:
                    if additional_email.email not in unique_emails:
                        unique_emails.append(additional_email.email)

        return unique_emails
    
    def build_email_body_for_job_creation(self, job: Job,
                         services: [Service],
                         retainer_services: [RetainerService],
                         email_util: EmailUtil):
        
        etd = 'Not Specified'
        if job.estimatedETD:
            etd = job.estimatedETD.strftime('%m/%d/%y %H:%M')

        eta = 'Not Specified'
        if job.estimatedETA:
            eta = job.estimatedETA.strftime('%m/%d/%y %H:%M')
        
        complete_before = 'Not Specified'
        if job.completeBy:
            complete_before = job.completeBy.strftime('%m/%d/%y %H:%M')

        if job.on_site:
            eta = 'On Site'

        service_names = ''
        for service in services:
            service_names += service.name + ', '

        # remove the last comma from service_names if not empty
        if service_names:
            service_names = service_names[:-2]

        retainer_service_names = ''
        for retainer_service in retainer_services:
            retainer_service_names += retainer_service.name + ', '

        # remove the last comma from retainer_service_names if not empty
        if retainer_service_names:
            retainer_service_names = retainer_service_names[:-2]

        message = str(job.id) + '-' + job.tailNumber
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        body = f'''
                <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Customer Job Request</div>
                <a href="http://livetakeoff.com/shared/jobs/{base64_message}/confirm" style="display: inline-block; padding: 0.5625rem 1.125rem; margin: 0 5px; font-size: 1.5rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.375rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #fff; background-color: #007bff; border-color: #007bff;">CONFIRM</a>
                <a href="http://livetakeoff.com/jobs/{job.id}/details" style="display: inline-block; padding: 0.5625rem 1.125rem; margin: 0 5px; font-size: 1.5rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.375rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #212529; background-color: #f8f9fa; border-color: #f8f9fa;">EDIT</a>

                <div style="margin-bottom:20px"></div>
                <table style="border-collapse: collapse">
                    <tr>
                        <td style="padding:15px">Customer</td>
                        <td style="padding:15px">{job.customer.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Job PO</td>
                        <td style="padding:15px">{job.purchase_order}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Tail</td>
                        <td style="padding:15px">{job.tailNumber}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Airport</td>
                        <td style="padding:15px">{job.airport.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">FBO</td>
                        <td style="padding:15px">{job.fbo.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Arrival</td>
                        <td style="padding:15px">{eta}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Departure</td>
                        <td style="padding:15px">{etd}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Complete Before</td>
                        <td style="padding:15px">{complete_before}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Services</td>
                        <td style="padding:15px">{service_names}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Retainer Services</td>
                        <td style="padding:15px">{retainer_service_names}</td>
                    </tr>
                </table>
                <div style="margin-top:20px;padding:5px;font-weight: 700;"></div>
                '''

        body += email_util.getEmailSignature()

        return body
    
    def schedule_acceptance_emails(self, job_id):
        while True:
            # Wait for 30 minutes before executing again
            time.sleep(30 * 60)

            #Refetch job from database
            job = Job.objects.get(pk=job_id)

            if job.status != 'S':
                return
            
            # check if this job has a tag with name 'Vendor Accepted'
            for job_tag in job.tags.all():
                if job_tag.tag.name == 'Vendor Accepted':
                    return
           
            last_project_managers_notified = LastProjectManagersNotified.objects.filter(job=job).all()

            # Check if all of the last_project_managers_notified have been notified already 3 times in JobacceptanceNotification. If they have, you can exit the function
            all_notified = True
            for last_project_manager_notified in last_project_managers_notified:
                job_acceptance_notifications = JobAcceptanceNotification.objects.filter(job=job, project_manager=last_project_manager_notified.project_manager).all()

                if job_acceptance_notifications.count() < 3:
                    all_notified = False
                    break

            if all_notified:
                return
            
            email_util = EmailUtil()

            for last_project_manager_notified in last_project_managers_notified:
                
                project_manager = User.objects.get(pk=last_project_manager_notified.project_manager_id)

                # Get the last notification attempt
                job_acceptance_notification = JobAcceptanceNotification.objects.filter(job=job, project_manager=project_manager).order_by('-attempt').first()

                if job_acceptance_notification.attempt < 3:
                    unique_emails = []
                    if project_manager.email not in unique_emails:
                        unique_emails.append(project_manager.email)

                        additional_emails = UserEmail.objects.filter(user=project_manager)
                        for additional_email in additional_emails:
                            if additional_email.email not in unique_emails:
                                unique_emails.append(additional_email.email)


                    body = self.build_email_body_for_recurrent_acceptance(job)
                    body += email_util.getEmailSignature()

                    attempt = job_acceptance_notification.attempt + 1

                    if attempt == 2:
                        subject = f'Second Notification - {job.tailNumber} - Job ASSIGNED - Review and ACCEPT it or RETURN it as soon as possible.'

                    elif attempt == 3:
                        subject = f'Last Notification - {job.tailNumber} - Job ASSIGNED - Review and ACCEPT it or RETURN it as soon as possible.'

                    for email in unique_emails:
                        email_util.send_email(email, subject, body)

                    JobAcceptanceNotification.objects.create(job=job, project_manager=project_manager, attempt=attempt)
    

    def build_email_body(self, job: Job,
                         title: str,
                         comment: str,
                         email_util: EmailUtil):
        
        service_names = ''
        for service in job.job_service_assignments.all():
            service_names += service.service.name + ', '

        if service_names:
            service_names = service_names[:-2]

        retainer_service_names = ''
        for retainer in job.job_retainer_service_assignments.all():
            retainer_service_names += retainer.retainer_service.name + ', '
        
        if retainer_service_names:
            retainer_service_names = retainer_service_names[:-2]

        body = f'''
                <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">{title}</div>
                <a href="http://livetakeoff.com/jobs/{job.id}/details" style="display: inline-block; padding: 0.5625rem 1.125rem; margin: 0 5px; font-size: 1.5rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.375rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #212529; background-color: #f8f9fa; border-color: #f8f9fa;">REVIEW</a>

                <div style="margin-bottom:20px"></div>
                <table style="border-collapse: collapse">
                    <tr>
                        <td style="padding:15px">Customer</td>
                        <td style="padding:15px">{job.customer.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Job PO</td>
                        <td style="padding:15px">{job.purchase_order}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Tail</td>
                        <td style="padding:15px">{job.tailNumber}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Airport</td>
                        <td style="padding:15px">{job.airport.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">FBO</td>
                        <td style="padding:15px">{job.fbo.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Arrival</td>
                        <td style="padding:15px">{job.arrival_formatted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Departure</td>
                        <td style="padding:15px">{job.departure_formatted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Complete Before</td>
                        <td style="padding:15px">{job.complete_before_formatted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Services</td>
                        <td style="padding:15px">{service_names}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Retainer Services</td>
                        <td style="padding:15px">{retainer_service_names}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Comment</td>
                        <td style="padding:15px">{comment}</td>
                    </tr>
                </table>
                <div style="margin-top:20px;padding:5px;font-weight: 700;"></div>
                '''

        body += email_util.getEmailSignature()

        return body