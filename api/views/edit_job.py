import django
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import (JobEditSerializer)
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal

from api.notification_util import NotificationUtil
from api.email_util import EmailUtil

from ..models import (
    Job,
    JobStatusActivity,
    JobCommentCheck,
    ServiceActivity,
    RetainerServiceActivity,
    Tag,
    JobTag,
    PriceListEntries,
    UserEmail
    )


class EditJobView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        job = get_object_or_404(Job, pk=id)

        if not self.can_edit_job(request.user, job):
            return Response({'error': 'You do not have permission to edit a job'}, status=status.HTTP_403_FORBIDDEN)
        
        current_status = job.status
        current_price = job.price
        current_airport = job.airport.id
        current_fbo = job.fbo.id
        current_tailNumber = job.tailNumber
        current_estimatedETD = job.estimatedETD
        current_estimatedETA = job.estimatedETA
        current_completeBy = job.completeBy

        # if request.data['price'] is null or empty, set it to job.price
        if not request.data.get('price'):
            request.data['price'] = job.price

        # ensure the tailNumber does not have trailing spaces or leading spaces
        request.data['tailNumber'] = request.data['tailNumber'].strip()

        serializer = JobEditSerializer(job, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            saved_job = Job.objects.get(pk=id)

            if request.user.is_superuser \
             or request.user.is_staff \
             or request.user.groups.filter(name='Account Managers').exists():
                saved_job.internal_additional_cost = request.data.get('internal_additional_cost', saved_job.internal_additional_cost)
                
                if saved_job.vendor:
                    vendor_charge = request.data.get('vendor_charge', saved_job.vendor_charge)
                    vendor_additional_cost = request.data.get('vendor_additional_cost', saved_job.vendor_additional_cost)

                    saved_job.vendor_charge = vendor_charge
                    saved_job.vendor_additional_cost = vendor_additional_cost
                    saved_job.subcontractor_profit = saved_job.price - Decimal(str(vendor_charge + vendor_additional_cost))

                saved_job.save(update_fields=['internal_additional_cost', 'vendor_charge', 'vendor_additional_cost', 'subcontractor_profit'])


            if current_estimatedETD != saved_job.estimatedETD:
                JobStatusActivity.objects.create(job=job, user=request.user,
                                                 status=serializer.data['status'], activity_type='E')
                
                departure_formatted_date = 'Not Specified'
                if saved_job.estimatedETD:
                    departure_formatted_date = serializer.data['estimatedETD']
                    departure_formatted_date += ' LT'

                saved_job.departure_formatted_date = departure_formatted_date


            if current_estimatedETA != saved_job.estimatedETA:
                JobStatusActivity.objects.create(job=job, user=request.user,
                                    status=serializer.data['status'], activity_type='A')
                
                arrival_formatted_date = 'Not Specified'
                if saved_job.estimatedETA:
                    arrival_formatted_date = serializer.data['estimatedETA']
                    arrival_formatted_date += ' LT'

                if saved_job.on_site:
                    arrival_formatted_date = 'On Site'
                
                saved_job.arrival_formatted_date = arrival_formatted_date


            if current_completeBy != saved_job.completeBy:
                JobStatusActivity.objects.create(job=job, user=request.user,
                                    status=serializer.data['status'], activity_type='B')
                
                complete_by_formatted_date = 'Not Specified'
                if saved_job.completeBy:
                    complete_by_formatted_date = serializer.data['completeBy']
                    complete_by_formatted_date += ' LT'
                
                saved_job.complete_before_formatted_date = complete_by_formatted_date


            if current_airport != serializer.data['airport']:
                JobStatusActivity.objects.create(job=job, user=request.user,
                                    status=serializer.data['status'], activity_type='O')


            if current_fbo != serializer.data['fbo']:
                JobStatusActivity.objects.create(job=job, user=request.user,
                                    status=serializer.data['status'], activity_type='F')


            if current_tailNumber != serializer.data['tailNumber']:
                JobStatusActivity.objects.create(job=job, user=request.user,
                                    status=serializer.data['status'], activity_type='T')
                
            saved_job.save()


            # only non-customer users can edit this part
            if not request.user.profile.customer:
                JobTag.objects.filter(job=job).delete()
                tag_ids = request.data['tags']
                tags = []
                if tag_ids:
                    tags = Tag.objects.filter(id__in=tag_ids)

                for tag in tags:
                    JobTag.objects.create(job=job, tag=tag)

                new_status = serializer.data['status']

                if current_status != new_status:

                    if new_status == 'C':
                        job_comment_checks = JobCommentCheck.objects.filter(job=job)

                        if job_comment_checks:
                            job_comment_checks.delete()

                        #Send a notification to all admins and account managers
                        notification_util = NotificationUtil()
                        admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

                        for admin in admins:
                            # get the phone number of the admin
                            phone_number = admin.profile.phone_number
                            if phone_number:
                                message = f'Job {job.purchase_order} for tail number {job.tailNumber} has been COMPLETED.'
                                
                                notification_util.send(message, phone_number.as_e164)

                        
                        # send an email notification to the customer user if the job was created by a customer user
                        if job.created_by.profile.customer \
                                and job.created_by.profile.email_notifications:
                            
                            title = f'[{job.tailNumber}] Job COMPLETED'
                            link = f'http://livetakeoff.com/jobs/{job.id}/details'

                            body = f'''
                            <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Job has been COMPLETED</div>
                            
                            <div>
                                <div style="padding:5px;font-weight: 700;">Tail Number</div>
                                <div style="padding:5px">{job.tailNumber}</div>
                                <div style="padding:5px;font-weight: 700;">Airport</div>
                                <div style="padding:5px">{job.airport.name}</div>
                                <div style="padding:5px;font-weight: 700;">Aircraft</div>
                                <div style="padding:5px">{job.aircraftType.name}</div>
                                <div style="padding:5px;font-weight: 700;">Link</div>
                                <div style="padding:5px">{link}</div>
                            </div>
                            '''

                            email_util = EmailUtil()

                            body += email_util.getEmailSignature()

                            if job.created_by.email:
                                email_util.send_email(job.created_by.email, title, body)

                            #fetch entries of UserEmail for the customer user and send an email to each email address
                            user_emails = UserEmail.objects.filter(user=job.created_by)

                            for user_email in user_emails:
                                if user_email.email:
                                    email_util.send_email(user_email.email, title, body)


                        #unassign all services and retainer services
                        for service in job.job_service_assignments.all():
                            service.status == 'U'
                            service.project_manager = None
                            service.save(update_fields=['project_manager', 'status'])

                            if not ServiceActivity.objects.filter(job=job, service=service.service, status='C').exists():
                                ServiceActivity.objects.create(job=job,
                                                                service=service.service,
                                                                status='C',
                                                                project_manager=request.user)


                        for retainer_service in job.job_retainer_service_assignments.all():
                            retainer_service.status = 'U'
                            retainer_service.project_manager = None
                            retainer_service.save(update_fields=['project_manager', 'status'])

                            if not RetainerServiceActivity.objects.filter(job=job, retainer_service=retainer_service.retainer_service, status='C').exists():
                                RetainerServiceActivity.objects.create(job=job,
                                                                        retainer_service=retainer_service.retainer_service,
                                                                        status='C',
                                                                        project_manager=request.user)


                        job.completion_date = datetime.now()
                        job.save()
                    
                    elif new_status == 'T':
                        #unassign all services and retainer services
                        for service in job.job_service_assignments.all():
                            service.status = 'U'
                            service.project_manager = None
                            service.save(update_fields=['project_manager', 'status'])

                        for retainer_service in job.job_retainer_service_assignments.all():
                            retainer_service.status = 'U'
                            retainer_service.project_manager = None
                            retainer_service.save(update_fields=['project_manager', 'status'])

                    elif new_status == 'I':
                        # calculate the price for each service associated with this job
                        for service in job.job_service_assignments.all():
                            service_price = 0
                            customer_settings = job.customer.customer_settings
                            aircraft_type = job.aircraftType
                            service_id = service.service.id

                            try:
                                price_list_entry = PriceListEntries.objects.get(
                                                                price_list_id=customer_settings.price_list_id,
                                                                aircraft_type_id=aircraft_type.id,
                                                                service_id=service_id)
                            
                                service_price = price_list_entry.price

                                # Update ServiceActivity for the corresponding service_price with the service_price
                                service_activity = ServiceActivity.objects.filter(job=job, service_id=service_id, status='C').first()

                                service_activity.price = service_price

                                service_activity.save(update_fields=['price'])

                            except PriceListEntries.DoesNotExist:
                                continue


                    JobStatusActivity.objects.create(job=job, user=request.user, status=new_status)

                if current_price != serializer.data['price']:
                    job.is_auto_priced = False
                    
                    # reset fees applied to 0
                    job.travel_fees_amount_applied = 0
                    job.fbo_fees_amount_applied = 0
                    job.vendor_higher_price_amount_applied = 0
                    job.management_fees_amount_applied = 0

                    job.save()

                    JobStatusActivity.objects.create(job=job, user=request.user, status='P', activity_type='P', price=serializer.data['price'])


            response = {
                'id': job.id,
            }

            return Response(response, status.HTTP_200_OK)

        return Response({'error': 'Missing Required Fields'}, status.HTTP_400_BAD_REQUEST)



    def can_edit_job(self, user, job):
        """
        Check if the user has permission to edit a job.
        """
        # if the user is a customer, he/she can edit the job is the job.customer matches its customer
        if user.profile.customer and user.profile.customer == job.customer:
            return True

        if user.is_superuser \
             or user.is_staff \
             or user.groups.filter(name='Internal Coordinators').exists() \
             or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False
