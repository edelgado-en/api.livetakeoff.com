from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

import base64

import threading
import time

from ..models import (
    JobServiceAssignment,
    Job,
    JobRetainerServiceAssignment,
    JobStatusActivity,
    EstimatedServiceTime,
    Service,
    RetainerService,
    ServiceActivity,
    UserAvailableAirport,
    JobTag,
    UserEmail,
    LastProjectManagersNotified,
    JobAcceptanceNotification
    )

from ..pricebreakdown_service import PriceBreakdownService

from ..serializers import (
                    JobServiceAssignmentSerializer,
                    JobRetainerServiceAssignmentSerializer,
                    BasicUserSerializer
                )

from api.notification_util import NotificationUtil
from api.email_util import EmailUtil

class JobServiceAssignmentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        assignments = JobServiceAssignment \
                                .objects.select_related('service') \
                                .filter(job=job) \
                                .order_by('created_at')

        retainer_assignments = JobRetainerServiceAssignment \
                                    .objects.select_related('retainer_service') \
                                    .filter(job=job) \
                                    .order_by('created_at')

        # Use a different serializer because you don't need the profile part
        service_assignments = JobServiceAssignmentSerializer(assignments, many=True)
        retainer_service_assignments = JobRetainerServiceAssignmentSerializer(retainer_assignments, many=True)

        airport = job.airport

        # get project managers and their availability
        project_managers = User.objects.filter(groups__name='Project Managers', is_active=True)

        for project_manager in project_managers:
            # Check if this project_manager has any entries in UserAvailableAirport table. If there are entries, then check if the airport for this job is in the list of available airports for this project manager
            # if not, then remove the project manager from the list of project managers
            # if there are no entries at all, then the project manager is available for all airports
            user_available_airports = UserAvailableAirport.objects.filter(user=project_manager).all()

            if user_available_airports:
                airport_ids = []
                for user_available_airport in user_available_airports:
                    airport_ids.append(user_available_airport.airport.id)

                if airport.id not in airport_ids:
                    project_managers = project_managers.exclude(id=project_manager.id)


            # Get the in-process assignments for this user for other jobs
            assignments_in_process = project_manager \
                                       .job_service_assignments \
                                       .select_related('job') \
                                       .select_related('service') \
                                       .filter(Q(status='W') | Q(status='A')) \
                                       .filter(~Q(job=job))

            if assignments_in_process.count() == 0:
                project_manager.availability = 'available'
                continue

            # if you are here, that means you are either busy or available soon

            # the available soon is calculated after iterating through the assignments in process
            # all you have to do in the loop is add up the hours of the service in process
            # so that then you can compare

            # you get all the wip services for a user with their corresponding aircraft types. You are just collecting
            # so that you can add up the hours in total
            # then outside the this loop, you can say this a project manager has x hours to be available 

            total_estimated_work_hours = 0

            for assignment_in_process in assignments_in_process:
                job_in_process = assignment_in_process.job


                # Get the latest assignment
                latest_assignment_activity =  JobStatusActivity.objects \
                                                                .filter(job=job_in_process, status='A') \
                                                                .order_by('-timestamp') \
                                                                .first()
                
                # account for no activity. Maybe someone is adding from admin view
                if latest_assignment_activity is None:
                    continue


                # get estimated hours for this service/aircraftType
                try:
                    estimated_time = EstimatedServiceTime.objects.get(service=assignment_in_process.service,
                                                                  aircraft_type=job_in_process.aircraftType)        

                    if estimated_time is None:
                        continue

                    # keep going

                except EstimatedServiceTime.DoesNotExist:
                    # do something here
                    pass



            # Because you don't have estimated times, you are unavailable to calculate available soon
            # just say it is busy
            if total_estimated_work_hours == 0:
                project_manager.availability = 'busy'


            # TODO: YOU HAVE TO ALSO CHECK IN RETAINER SERVICES
            # you the aircraft type of the job and the service to check the estimated time


        users = BasicUserSerializer(project_managers, many=True)

        response = {
            'services': service_assignments.data,
            'retainer_services': retainer_service_assignments.data,
            'project_managers': users.data
        }

        return Response(response, status.HTTP_200_OK)


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

        notification_util = NotificationUtil()

        message = f'Job ASSIGNED to you\n• {job.airport.initials}\n• {job.tailNumber}\n• {job.fbo.name}\n'

        for phone_number in unique_phone_numbers:
            notification_util.send(message, phone_number.as_e164)

        subject = f'{job.tailNumber} - Job ASSIGNED - Review and ACCEPT it or RETURN it as soon as possible.'

        # remove the last comma from service_names if not empty
        if service_names:
            service_names = service_names[:-2]

        # remove the last comma from retainer_service_names if not empty
        if retainer_service_names:
            retainer_service_names = retainer_service_names[:-2]

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

        for email in unique_emails:
            email_util.send_email(email, subject, body)


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

    