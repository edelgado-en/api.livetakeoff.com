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

from ..models import (
    Job,
    JobStatusActivity,
    JobCommentCheck,
    ServiceActivity,
    RetainerServiceActivity,
    Tag,
    JobTag,
    PriceListEntries,
    InvoicedService,
    InvoicedDiscount,
    InvoicedFee,
    JobFollowerEmail,
    TailIdent,
    UserCustomer
    )

from api.email_notification_service import EmailNotificationService
from api.sms_notification_service import SMSNotificationService
from api.pricebreakdown_service import PriceBreakdownService

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
                
                vendor_id = request.data.get('vendor', saved_job.vendor_id)
                vendor_charge = request.data.get('vendor_charge', saved_job.vendor_charge)
                vendor_additional_cost = request.data.get('vendor_additional_cost', saved_job.vendor_additional_cost)

                saved_job.vendor_id = vendor_id
                saved_job.vendor_charge = vendor_charge
                saved_job.vendor_additional_cost = vendor_additional_cost
                saved_job.subcontractor_profit = saved_job.price - Decimal(str(vendor_charge + vendor_additional_cost))

                saved_job.save(update_fields=['internal_additional_cost', 'vendor_charge', 'vendor_additional_cost', 'subcontractor_profit'])

                ident = request.data.get('ident')

                # if ident is not None, create or update the tail ident in TailIdent for this saved_job.tailNumber
                if ident is not None:
                    # if ident is empty, delete the tail ident
                    if ident == '':
                        TailIdent.objects.filter(tail_number=saved_job.tailNumber).delete()
                    else:
                        tail_ident = TailIdent.objects.filter(tail_number=saved_job.tailNumber).first()

                        if tail_ident:
                            tail_ident.ident = ident
                            tail_ident.save(update_fields=['ident'])
                        else:
                            TailIdent.objects.create(tail_number=saved_job.tailNumber, ident=ident)


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

                JobFollowerEmail.objects.filter(job=job).delete()
                follower_emails = request.data.get('followerEmails', [])
                for email in follower_emails:
                    JobFollowerEmail.objects.create(job=job, email=email)

                new_status = serializer.data['status']

                if current_status != new_status:

                    if new_status == 'C':
                        job_comment_checks = JobCommentCheck.objects.filter(job=job)

                        if job_comment_checks:
                            job_comment_checks.delete()

                        SMSNotificationService().send_job_completed_notification(job, request.user)

                        EmailNotificationService().send_job_completed_notification(job, request.user)

                        EmailNotificationService().send_job_completed_notification_to_followers(job)

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
                        JobStatusActivity.objects.filter(job=job, status='N').delete()

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

                    elif new_status == 'N':
                        JobStatusActivity.objects.filter(job=job, status='I').delete()


                    JobStatusActivity.objects.create(job=job, user=request.user, status=new_status)

                if current_price != serializer.data['price']:
                    job.is_auto_priced = False
                    
                    # reset fees applied to 0
                    job.travel_fees_amount_applied = 0
                    job.fbo_fees_amount_applied = 0
                    job.vendor_higher_price_amount_applied = 0
                    job.management_fees_amount_applied = 0
                    job.discounted_price = 0
                    job.invoiced_price_list = None

                    job.save()

                    InvoicedService.objects.filter(job=job).delete()
                    InvoicedFee.objects.filter(job=job).delete()
                    InvoicedDiscount.objects.filter(job=job).delete()

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

        if user.profile.customer:
            if user.profile.customer == job.customer:
                return True

            # Get extra customers from UserCustomer for this user
            user_customers = UserCustomer.objects.filter(user=user).all()
            for user_customer in user_customers:
                if user_customer.customer == job.customer:
                    return True

        if user.is_superuser \
             or user.is_staff \
             or user.groups.filter(name='Internal Coordinators').exists() \
             or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False
