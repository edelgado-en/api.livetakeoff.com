from django.shortcuts import get_object_or_404
from django.db.models import Q, OuterRef, Exists
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
import base64
import requests
import threading

from ..models import (
    JobServiceAssignment,
    Job,
    JobRetainerServiceAssignment,
    JobStatusActivity,
    Service,
    ServiceActivity,
    UserAvailableAirport,
    JobTag,
    UserEmail,
    LastProjectManagersNotified,
    JobAcceptanceNotification,
    JobStatusActivity
    )

from ..pricebreakdown_service import PriceBreakdownService

from api.email_notification_service import EmailNotificationService
from api.sms_notification_service import SMSNotificationService

from ..serializers import (
                    JobServiceAssignmentSerializer,
                    JobRetainerServiceAssignmentSerializer,
                    BasicUserSerializer
                )

class JobServiceAssignmentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        assignments = JobServiceAssignment.objects.select_related('service').filter(job=job).order_by('created_at')
        retainer_assignments = JobRetainerServiceAssignment.objects.select_related('retainer_service').filter(job=job).order_by('created_at')

        service_assignments = JobServiceAssignmentSerializer(assignments, many=True)
        retainer_service_assignments = JobRetainerServiceAssignmentSerializer(retainer_assignments, many=True)

        airport = job.airport
        is_master_vendor_pm = self.request.user.profile.master_vendor_pm

        # Base query: all active Project Managers (filtered by vendor if needed)
        base_pm_query = User.objects.filter(groups__name='Project Managers', is_active=True)
        if is_master_vendor_pm:
            base_pm_query = base_pm_query.filter(profile__vendor=self.request.user.profile.vendor)

        # Subquery: check if a user has a specific airport in their availability
        airport_match = UserAvailableAirport.objects.filter(user=OuterRef('pk'), airport=airport)
        has_any_airports = UserAvailableAirport.objects.filter(user=OuterRef('pk'))

        # Final queryset: either the user has no airports mapped, or has the current airport mapped
        eligible_pms = base_pm_query.annotate(
            has_airport=Exists(airport_match),
            has_any_airports=Exists(has_any_airports),
        ).filter(
            Q(has_airport=True) | Q(has_any_airports=False)
        )

        users = BasicUserSerializer(eligible_pms, many=True)

        preferred_project_manager_id = None
        if job.airport.preferred_project_manager and eligible_pms.filter(id=job.airport.preferred_project_manager.id).exists():
            preferred_project_manager_id = job.airport.preferred_project_manager.id

        return Response({
            'services': service_assignments.data,
            'preferred_project_manager_id': preferred_project_manager_id,
            'retainer_services': retainer_service_assignments.data,
            'project_managers': users.data
        }, status=status.HTTP_200_OK)


    def post(self, request, id):

        job = get_object_or_404(Job, pk=id)
        service = get_object_or_404(Service, pk=request.data['service_id'])

        user_id = request.data.get('user_id', None)
        project_manager = None

        if user_id is not None:
            project_manager = get_object_or_404(User, pk=user_id)
            status = 'A'
        else:
            status = 'U'

        # if the job is in status W, then change the assignment status to W
        if job.status == 'W':
            status = 'W'
        elif job.status == 'I' or job.status == 'C':
            status = 'C'
            # if the job is already invoice or completed and we are adding a new service with an specified project manager, we create
            # an activity for the service with the status 'C' so that the service report is accurate
            if project_manager is not None:
                ServiceActivity.objects.create(job=job, service=service, project_manager=project_manager, status='C')


        assignment = JobServiceAssignment(job=job, project_manager=project_manager, service=service, status=status)
        assignment.save()

        JobStatusActivity.objects.create(job=job, status=status, activity_type='C',
                                         user=request.user, service_name=service.name)

        # re-fetch job and update price after deleting service only if the job is auto_priced  and not invoiced
        
        updated_job = Job.objects.get(pk=job.id)
        
        if job.is_auto_priced and job.status != 'I':
            price_breakdown = PriceBreakdownService().get_price_breakdown(updated_job)
            updated_job.price = price_breakdown.get('totalPrice')
            updated_job.travel_fees_amount_applied = price_breakdown.get('total_travel_fees_amount_applied')
            updated_job.fbo_fees_amount_applied = price_breakdown.get('total_fbo_fees_amount_applied')
            updated_job.vendor_higher_price_amount_applied = price_breakdown.get('total_vendor_higher_price_amount_applied')
            updated_job.management_fees_amount_applied = price_breakdown.get('total_management_fees_amount_applied')

            updated_job.save()

        if job.status != 'I':
            external_vendor = None
            for service_assignment in updated_job.job_service_assignments.all():
                if service_assignment.vendor:
                    external_vendor = service_assignment.vendor
            
            updated_job.vendor = external_vendor

            # adjust the subcontractor_profit if there is a external_vendor
            if external_vendor:
                vendor_charge = updated_job.vendor_charge if updated_job.vendor_charge else 0
                vendor_additional_cost = updated_job.vendor_additional_cost if updated_job.vendor_additional_cost else 0
                updated_job.subcontractor_profit = updated_job.price - (vendor_charge + vendor_additional_cost)

            updated_job.save()

        serializer = JobServiceAssignmentSerializer(assignment)

        return Response(serializer.data)


    def put(self, request, id):
        job = get_object_or_404(Job, pk=id)

        at_least_one_service_assigned = False
        external_vendor = None

        unique_phone_numbers = []
        unique_emails = []
        unique_project_manager_ids_notified = []
        unique_expo_tokens = []

        service_names = ''
        retainer_service_names = ''

        # if all services are assigned and the job status is less than assigned, then set the job status to assigned
        for service in request.data['services']:
            
            assignment =  JobServiceAssignment.objects \
                                              .get(pk=service['assignment_id'])
            
            if service['user_id']:
                user = User.objects.get(pk=service['user_id'])
                assignment.project_manager = user
                
                if job.status != 'C' and job.status != 'I' and job.status != 'T':
                    assignment.status = 'A'

                    service_names += assignment.service.name + ', '

                    # add the phone number to the list of unique phone numbers
                    if user.profile.phone_number:
                        if user.profile.phone_number not in unique_phone_numbers:
                            unique_phone_numbers.append(user.profile.phone_number)

                    if user.profile.expo_push_token:
                        if user.profile.expo_push_token not in unique_expo_tokens:
                            unique_expo_tokens.append(user.profile.expo_push_token)

                    if user.profile.enable_accept_jobs:
                        if user.email not in unique_emails:
                            unique_emails.append(user.email)

                            if user.id not in unique_project_manager_ids_notified:
                                unique_project_manager_ids_notified.append(user.id)

                        additional_emails = UserEmail.objects.filter(user=user)
                        for additional_email in additional_emails:
                            if additional_email.email not in unique_emails:
                                unique_emails.append(additional_email.email)

                    at_least_one_service_assigned = True
                
                # Check if this user.profile.vendor is external vendor and set it external_vendor
                if user.profile.vendor:
                    if user.profile.vendor.is_external:
                        external_vendor = user.profile.vendor
                        assignment.vendor = external_vendor

            else :
                assignment.status = 'U'
                assignment.project_manager = None
                assignment.vendor = None

            assignment.save()

        for retainer_service in request.data['retainer_services']:
            
            retainer_assignment =  JobRetainerServiceAssignment.objects \
                                                               .get(pk=retainer_service['assignment_id'])
            
            if retainer_service['user_id']:
                user = User.objects.get(pk=retainer_service['user_id'])
                retainer_assignment.project_manager = user

                if job.status != 'C' and job.status != 'I' and job.status != 'T':
                    retainer_assignment.status = 'A'

                    retainer_service_names += retainer_assignment.retainer_service.name + ', '

                    # add the phone number to the list of unique phone numbers
                    if user.profile.phone_number:
                        if user.profile.phone_number not in unique_phone_numbers:
                            unique_phone_numbers.append(user.profile.phone_number)

                    if user.profile.expo_push_token:
                        if user.profile.expo_push_token not in unique_expo_tokens:
                            unique_expo_tokens.append(user.profile.expo_push_token)

                    if user.profile.enable_accept_jobs:
                        if user.email not in unique_emails:
                            unique_emails.append(user.email)

                            if user.id not in unique_project_manager_ids_notified:
                                unique_project_manager_ids_notified.append(user.id)

                        additional_emails = UserEmail.objects.filter(user=user)
                        for additional_email in additional_emails:
                            if additional_email.email not in unique_emails:
                                unique_emails.append(additional_email.email)

                    at_least_one_service_assigned = True
                
                # Check if this user.profile.vendor is external vendor and set it external_vendor
                if user.profile.vendor:
                    if user.profile.vendor.is_external:
                        external_vendor = user.profile.vendor
                        retainer_assignment.vendor = external_vendor

            else :
                retainer_assignment.status = 'U'
                retainer_assignment.project_manager = None
                retainer_assignment.vendor = None

            retainer_assignment.save()


        # if there is at least one service assigned, then set the status to assigned
        current_status = job.status
        
        job.vendor = external_vendor

        if at_least_one_service_assigned:
            if current_status == 'A' or current_status == 'U':
                job.status = 'S' # assigned

                JobStatusActivity.objects.create(job=job, status='S', user=request.user)
            
            # if there is a JobTag with the name 'Vendor Accepted' then delete it
            try:
                job_tag = JobTag.objects.get(job=job, tag__name='Vendor Accepted')
                job_tag.delete()
            except JobTag.DoesNotExist:
                pass

            job.save()

        # if none of the services are assigned and the job status is S or W, then set the job status to A
        if not at_least_one_service_assigned and (current_status == 'S' or current_status == 'W'):
            job.status = 'A'
            job.save()

            #record JobStatusActivity X PM Unassigned
            JobStatusActivity.objects.create(job=job, status='X', user=request.user)

        SMSNotificationService().send_job_assigned_notification(job, unique_phone_numbers)

        EmailNotificationService().send_job_assigned_notification(job, unique_emails, service_names, retainer_service_names)

        # send push notifications
        message = f'Job ASSIGNED to you • {job.airport.initials} • {job.tailNumber} • {job.fbo.name}'
        for expo_token in unique_expo_tokens:
            self.send_push_notification(expo_token, message)

        if unique_project_manager_ids_notified:
            LastProjectManagersNotified.objects.filter(job=job).delete()

        for project_manager_id in unique_project_manager_ids_notified:
            LastProjectManagersNotified.objects.create(job=job, project_manager_id=project_manager_id)

            JobAcceptanceNotification.objects.create(job=job, project_manager_id=project_manager_id, attempt=1)

        if unique_project_manager_ids_notified:
            thread1 = threading.Thread(target=self.schedule_acceptance_emails, args=(job.id,))
            thread1.start()

        response = {
            'message': 'assigned succesfully'
        }

        return Response(response, status.HTTP_200_OK)


    def patch(self, request, id):
        """ 
        Complete assignment
        """
        job_service_assignment = get_object_or_404(JobServiceAssignment, pk=id)

        if not self.can_view_assignment(request.user, job_service_assignment):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobServiceAssignmentSerializer(job_service_assignment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            #save service activity
            ServiceActivity.objects.create(job=job_service_assignment.job,
                                           service=job_service_assignment.service,
                                           project_manager=request.user, status='C')

            # if all services and retainer services associated with this job are completed, then this job is a candidate to be completed
            # return a boolean to the front end to indicate if the job can be completed
            job = job_service_assignment.job
            # get all services and retainer services associated with this job
            services = JobServiceAssignment.objects.filter(job=job)
            retainer_services = JobRetainerServiceAssignment.objects.filter(job=job)
            
            # check if they are all completed
            all_completed = True
            for service in services:
                if service.status != 'C':
                    all_completed = False
                    break

            if all_completed:
                for retainer_service in retainer_services:
                    if retainer_service.status != 'C':
                        all_completed = False
                        break

            return Response({'can_complete_job': all_completed}, status=status.HTTP_200_OK)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, id):
        job_service_assignment = get_object_or_404(JobServiceAssignment, pk=id)

        # get job before deleting service
        job_id = job_service_assignment.job.id
        
        #create JobStatusActivity for the service removed
        JobStatusActivity.objects.create(job=job_service_assignment.job, status=job_service_assignment.job.status, activity_type='D',
                                         user=request.user, service_name=job_service_assignment.service.name)

        # delete the service activities associated with this service
        ServiceActivity.objects.filter(job=job_id, service=job_service_assignment.service).delete()

        job_service_assignment.delete()

        # fetch job and update price after deleting service
        job = Job.objects.get(pk=job_id)

        if job.is_auto_priced and job.status != 'I':
            price_breakdown = PriceBreakdownService().get_price_breakdown(job)
            job.price = price_breakdown.get('totalPrice')
            job.travel_fees_amount_applied = price_breakdown.get('total_travel_fees_amount_applied')
            job.fbo_fees_amount_applied = price_breakdown.get('total_fbo_fees_amount_applied')
            job.vendor_higher_price_amount_applied = price_breakdown.get('total_vendor_higher_price_amount_applied')
            job.management_fees_amount_applied = price_breakdown.get('total_management_fees_amount_applied')

        external_vendor = None
        for service_assignment in job.job_service_assignments.all():
            if service_assignment.vendor:
                external_vendor = service_assignment.vendor
        
        job.vendor = external_vendor

        # adjust the subcontractor_profit if there is a external_vendor
        if external_vendor:
            vendor_charge = job.vendor_charge if job.vendor_charge else 0
            vendor_additional_cost = job.vendor_additional_cost if job.vendor_additional_cost else 0
            job.subcontractor_profit = job.price - (vendor_charge + vendor_additional_cost)

        job.save()

        return Response({'message': 'Delete successfully'}, status.HTTP_200_OK)


    def can_view_assignment(self, user, job_service_assignment):
        if user.is_superuser \
           or user.is_staff \
           or user.groups.filter(name='Internal Coordinators').exists() \
           or user.groups.filter(name='Account Managers').exists():
           return True
           
        if job_service_assignment.project_manager.id == user.id:
            return True

        return False
    
    def build_email_body_for_recurrent_acceptance(self, job):
        message = str(job.id) + '-' + job.tailNumber
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        # Fetch the service assignments associated with this job
        service_names = ''

        for service in job.job_service_assignments.all():
            service_names += service.service.name + ', '

        if service_names:
            service_names = service_names[:-2]

        # Fetch the retainer service assignments associated with this job
        retainer_service_names = ''

        for retainer_service in job.job_retainer_service_assignments.all():
            retainer_service_names += retainer_service.retainer_service.name + ', '

        if retainer_service_names:
            retainer_service_names = retainer_service_names[:-2]

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
        
        return body
    
    def schedule_acceptance_emails(self, job_id):
        EmailNotificationService().schedule_acceptance_emails(job_id)

    def send_push_notification(self, expo_token, message):
        payload = {
            "to": expo_token,
            "sound": "default",
            "title": message,
            "body": message,
            "sound": "default"
        }
        
        requests.post("https://exp.host/--/api/v2/push/send", json=payload)

    