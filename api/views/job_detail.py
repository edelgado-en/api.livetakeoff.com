from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

import base64

from ..serializers import (
     JobDetailSerializer,
     )

from ..pricebreakdown_service import PriceBreakdownService

from ..models import (
        Job,
        JobServiceAssignment,
        JobRetainerServiceAssignment,
        JobPhotos,
        JobStatusActivity,
        JobCommentCheck,
        ServiceActivity,
        RetainerServiceActivity,
        UserEmail,
        JobFiles
    )


from twilio.rest import Client
import os

from api.notification_util import NotificationUtil
from api.email_util import EmailUtil


class JobDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        if not self.can_view_job(request.user, job):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        customer_settings = job.customer.customer_settings

        special_instructions = ''

        if customer_settings:
            special_instructions = customer_settings.special_instructions


        job.special_instructions = special_instructions


        job_service_assignments = []
        job_retainer_service_assignments = []

        # Services are shown depending on the user. If you are an account manager/admin OR a customer user,
        #  you can see all services
        # if you are a project manager, you can only see the services assigned to you
        if request.user.is_superuser \
            or request.user.is_staff \
            or (request.user.profile.customer and request.user.profile.customer == job.customer) \
            or request.user.groups.filter(name='Account Managers').exists() \
            or request.user.groups.filter(name='Internal Coordinators').exists():
                
                # return all services attached to this job
                service_assignments = job.job_service_assignments \
                                         .select_related('service') \
                                         .select_related('project_manager') \
                                         .all()
                
                for service_assignment in service_assignments:
                    p_manager = service_assignment.project_manager
                    if (p_manager is None):
                        p_manager = 'Not Assigned'
                    else:
                        p_manager = p_manager.username

                    s_assignment = {
                        'id': service_assignment.id,
                        'name': service_assignment.service.name,
                        'project_manager': p_manager,
                        'status': service_assignment.status,
                        'checklist_actions': service_assignment.service.checklistActions.all(),
                    }

                    job_service_assignments.append(s_assignment)

                # return all retainer services atached to this job
                retainer_service_assignments = job.job_retainer_service_assignments \
                                                  .select_related('retainer_service') \
                                                  .select_related('project_manager') \
                                                  .all()
                
                for retainer_service_assignment in retainer_service_assignments:
                    p_manager = retainer_service_assignment.project_manager
                    if (p_manager is None):
                        p_manager = 'Not Assigned'
                    else:
                        p_manager = p_manager.username

                    r_assignment = {
                        'id': retainer_service_assignment.id,
                        'name': retainer_service_assignment.retainer_service.name,
                        'project_manager': p_manager,
                        'status': retainer_service_assignment.status,
                        'checklist_actions': retainer_service_assignment.retainer_service.checklistActions.all(),
                    }

                    job_retainer_service_assignments.append(r_assignment)

        
        else:
            # return only the services assigned to the current user
            service_assignments = request.user.job_service_assignments \
                                              .select_related('service') \
                                              .filter(job=job) \
                                              .all()

            for service_assignment in service_assignments:
                s_assignment = {
                    'id': service_assignment.id,
                    'name': service_assignment.service.name,
                    'status': service_assignment.status,
                    'checklist_actions': service_assignment.service.checklistActions.all(),
                }

                job_service_assignments.append(s_assignment)
                

            # retainer services
            retainer_service_assignments = request.user.job_retainer_service_assignments \
                                                       .select_related('retainer_service') \
                                                       .filter(job=job).all()

            for retainer_service_assignment in retainer_service_assignments:
                r_assignment = {
                    'id': retainer_service_assignment.id,
                    'name': retainer_service_assignment.retainer_service.name,
                    'status': retainer_service_assignment.status,
                    'checklist_actions': retainer_service_assignment.retainer_service.checklistActions.all(),
                }

                job_retainer_service_assignments.append(r_assignment)

        
        job.service_assignments = job_service_assignments
        job.retainer_service_assignments = job_retainer_service_assignments

        job.total_photos = JobPhotos.objects.filter(job=job).count()

        # Check if the price of the job is different from the price of the services and update the job price
        if job.is_auto_priced and job.status != 'I' and job.status != 'T':
            price_breakdown = PriceBreakdownService().get_price_breakdown(job)
            price = price_breakdown.get('totalPrice')
            
            if price != job.price:
                job.price = price
                job.save()
            

        show_job_price = True

        # check the customer settings if the user is a customer user to check if show_job_price is True
        if request.user.profile.customer:
            show_job_price_at_customer_level = request.user.profile.customer.customer_settings.show_job_price

            if show_job_price_at_customer_level:
                show_job_price_at_customer_user_level = request.user.profile.show_job_price

                if show_job_price_at_customer_user_level:
                    show_job_price = True
                
                else:
                    show_job_price = False

            else:
                show_job_price = False

        
        # if you are a project manager, set the job price to None
        if request.user.groups.filter(name='Project Managers').exists():
            show_job_price = False

        if show_job_price is False:
            job.price = None

        message = str(job.id) + '-' + job.tailNumber
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        job.encoded_id = base64_message

        serializer = JobDetailSerializer(job, context={'request': request})

        return Response(serializer.data)


    def patch(self, request, id):
        job = get_object_or_404(Job, pk=id)

        if not self.can_view_job(request.user, job):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobDetailSerializer(job, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            if ('status' in request.data 
                    and (request.data['status'] == 'W' or request.data['status'] == 'C')):
                for service in job.job_service_assignments.all():
                    service.status = request.data['status']

                    if request.data['status'] == 'C':
                        service.status = 'U'
                        service.project_manager = None
                        service.save(update_fields=['status', 'project_manager'])
                    
                    else:
                        service.save(update_fields=['status'])

                        ServiceActivity.objects.create(job=job,
                                                       service=service.service,
                                                       status='W',
                                                       project_manager=request.user)


                for retainer_service in job.job_retainer_service_assignments.all():
                    retainer_service.status = request.data['status']

                    if request.data['status'] == 'C':
                        retainer_service.status = 'U'
                        retainer_service.project_manager = None
                        retainer_service.save(update_fields=['status', 'project_manager'])

                    else:
                        retainer_service.save(update_fields=['status'])

                        RetainerServiceActivity.objects.create(job=job,
                                                               retainer_service=retainer_service.retainer_service,
                                                               status='W',
                                                               project_manager=request.user)


            
            notification_util = NotificationUtil()
            
            #Send a notification to all admins and account managers
            admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))
            
            if 'status' in request.data and request.data['status'] == 'C':
                job_comment_checks = JobCommentCheck.objects.filter(job=job)

                if job_comment_checks:
                    job_comment_checks.delete()

                for admin in admins:
                    # get the phone number of the admin
                    phone_number = admin.profile.phone_number
                    if phone_number:
                        # send a text message
                        
                        #Adding a link is throwing a 30007 error in Twilio
                        #message = f'Job {job.purchase_order} for tail number {job.tailNumber} has been COMPLETED. Please review the job and close it out https://livetakeoff.com/completed/review/{job.id}'

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

                    if job.created_by.email:
                        email_util.send_email(job.created_by.email, title, body)

                    #fetch entries of UserEmail for the customer user and send an email to each email address
                    user_emails = UserEmail.objects.filter(user=job.created_by)

                    for user_email in user_emails:
                        if user_email.email:
                            email_util.send_email(user_email.email, title, body)

                # set the actual_completion_date to today
                job.completion_date = datetime.now()
                job.save()

                #unassign all services and retainer services
                for service in job.job_service_assignments.all():
                    service.status = 'U'
                    service.project_manager = None
                    service.save(update_fields=['project_manager', 'status'])

                    # save service activity only if it does not exists already for this job and service
                    if not ServiceActivity.objects.filter(job=job, service=service.service, status='C').exists():
                        ServiceActivity.objects.create(job=job,
                                                       service=service.service,
                                                       status='C',
                                                       project_manager=request.user)


                for retainer_service in job.job_retainer_service_assignments.all():
                    retainer_service.status = 'U'
                    retainer_service.project_manager = None
                    retainer_service.save(update_fields=['project_manager', 'status'])

                    #save retainer service activity only if it does not exists already for this job and service
                    if not RetainerServiceActivity.objects.filter(job=job, retainer_service=retainer_service.retainer_service, status='C').exists():
                        RetainerServiceActivity.objects.create(job=job,
                                                               retainer_service=retainer_service.retainer_service,
                                                               status='C',
                                                               project_manager=request.user)

            
            if 'status' in request.data and request.data['status'] == 'W':
                for admin in admins:
                    # get the phone number of the admin
                    phone_number = admin.profile.phone_number
                    if phone_number:
                        # send a text message
                        
                        #message = f'Job {job.purchase_order} for tail number {job.tailNumber} has been ACCEPTED by {request.user.username}. You can checkout the job at https://livetakeoff.com/jobs/{job.id}/details'

                        message = f'Job {job.purchase_order} for tail number {job.tailNumber} has been ACCEPTED by {request.user.username}.'
                        
                        notification_util.send(message, phone_number.as_e164)


            # Cancel job
            if 'status' in request.data and request.data['status'] == 'T':
                #unassign all services and retainer services
                for service in job.job_service_assignments.all():
                    service.status = 'U'
                    service.project_manager = None
                    service.save(update_fields=['project_manager', 'status'])

                for retainer_service in job.job_retainer_service_assignments.all():
                    retainer_service.status = 'U'
                    retainer_service.project_manager = None
                    retainer_service.save(update_fields=['project_manager', 'status'])


                for admin in admins:
                    # get the phone number of the admin
                    phone_number = admin.profile.phone_number
                    if phone_number:
                        # send a text message
                        #message = f'Job {job.purchase_order} for tail number {job.tailNumber} has been CANCELLED by {request.user.username}. You can checkout the job at https://livetakeoff.com/jobs/{job.id}/details'

                        message = f'Job {job.purchase_order} for tail number {job.tailNumber} has been CANCELLED by {request.user.username}.'
                        
                        notification_util.send(message, phone_number.as_e164)

            
            if 'status' in request.data:
                JobStatusActivity.objects.create(job=job, user=request.user, status=request.data['status'])
                
                job_status = request.data["status"]

                #we only notify customer for status A, W, C
                if job_status == 'A' or job_status == 'W' or job_status == 'C':
                    
                    # Get Status name
                    status_name = 'COMPLETED'
                    if job_status == 'A':
                        status_name = 'ACCEPTED'
                    elif job_status == 'W':
                        status_name = 'STARTED'
                    
                    
                    # if the job.requested_by is a customer user (check if userProfile has a customer specified), send an SMS notification to the customer if he/she has the sms_notification enabled in its UserProfile
                    if job.created_by.profile.customer and job.created_by.profile.sms_notifications:
                        # check if user has a phone number
                        phone_number = job.created_by.profile.phone_number

                        # check if the request_by is different than the user who is updating the job. Only send notification if the user is different
                        if phone_number and job.created_by != request.user:
                            notification_util.send(f'Job {job.purchase_order} for tail number {job.tailNumber} has been {status_name}.', phone_number.as_e164)


            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # MOVE THIS TO A SERVICE CLASS SO THAT YOU CAN USE IN OTHER VIEWS
    def can_view_job(self, user, job):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists() \
          or user.groups.filter(name='Internal Coordinators').exists():
           return True

        # check if the user is a customer by checking its profile and customer field. If the job's customer matches the user's customer, then the user can view the job
        if user.profile.customer and user.profile.customer == job.customer:
            return True



        # You are a Project Manager
        # Because the PM needs to be able to complete job after completing all the services
        # we allow them if they have at least one service associated with the job

        if job.status == 'I':
            return False
        
        if JobServiceAssignment.objects.filter(project_manager=user.id, job=job).exists() \
            or JobRetainerServiceAssignment.objects.filter(project_manager=user.id, job=job).exists():
            return True

        return False