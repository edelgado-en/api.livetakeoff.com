from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from ..models import (
    JobServiceAssignment,
    Job,
    JobRetainerServiceAssignment,
    JobStatusActivity,
    EstimatedServiceTime,
    Service,
    RetainerService,
    ServiceActivity,
    UserAvailableAirport
    )

from ..pricebreakdown_service import PriceBreakdownService

from ..serializers import (
                    JobServiceAssignmentSerializer,
                    JobRetainerServiceAssignmentSerializer,
                    BasicUserSerializer
                )

from api.notification_util import NotificationUtil


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

        project_manager = request.data['user_id']

        # TODO: add validation to ensure the service to be added does not already exist for this job

        # TODO: if all services are assigned, then the job status should be assigned if it less than assigned

        if project_manager is not None:
            project_manager = get_object_or_404(User, pk=request.data['user_id'])
            status = 'A'
        else:
            status = 'U'

        # if the job is in status W, then change the assignment status to W
        if job.status == 'W':
            status = 'W'

        assignment = JobServiceAssignment(job=job, project_manager=project_manager, service=service, status=status)
        assignment.save()

        # re-fetch job and update price after deleting service only if the job is auto_priced  and not invoiced
        
        updated_job = Job.objects.get(pk=job.id)
        
        if job.is_auto_priced and job.status != 'I':
            price_breakdown = PriceBreakdownService().get_price_breakdown(updated_job)
            updated_job.price = price_breakdown.get('totalPrice')

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

        # if all services are assigned and the job status is less than assigned, then set the job status to assigned
        for service in request.data['services']:
            
            assignment =  JobServiceAssignment.objects \
                                              .get(pk=service['assignment_id'])
            
            if service['user_id']:
                user = User.objects.get(pk=service['user_id'])
                assignment.project_manager = user
                assignment.status = 'A'

                # add the phone number to the list of unique phone numbers
                if user.profile.phone_number:
                    if user.profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user.profile.phone_number)

                # Check if this user.profile.vendor is external vendor and set it external_vendor
                if user.profile.vendor:
                    if user.profile.vendor.is_external:
                        external_vendor = user.profile.vendor
                        assignment.vendor = external_vendor

                at_least_one_service_assigned = True

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
                retainer_assignment.status = 'A'

                # add the phone number to the list of unique phone numbers
                if user.profile.phone_number:
                    if user.profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user.profile.phone_number)

                # Check if this user.profile.vendor is external vendor and set it external_vendor
                if user.profile.vendor:
                    if user.profile.vendor.is_external:
                        external_vendor = user.profile.vendor
                        retainer_assignment.vendor = external_vendor

                at_least_one_service_assigned = True

            else :
                retainer_assignment.status = 'U'
                retainer_assignment.project_manager = None
                retainer_assignment.vendor = None

            retainer_assignment.save()


        # if there is at least one service assigned, then set the status to assigned
        current_status = job.status

        if at_least_one_service_assigned:
            job.vendor = external_vendor

            if current_status == 'A' or current_status == 'U':
                job.status = 'S' # assigned

                JobStatusActivity.objects.create(job=job, status='S', user=request.user)
            
            job.save()

        # if none of the services are assigned and the job status is S or W, then set the job status to A
        if not at_least_one_service_assigned and (current_status == 'S' or current_status == 'W'):
            job.status = 'A'
            job.vendor = None
            job.save()

            #record JobStatusActivity X PM Unassigned
            JobStatusActivity.objects.create(job=job, status='X', user=request.user)

        # get the list of unique project managers and their phone numbers and send the job information with the app link as body

        notification_util = NotificationUtil()

        # Adding the link is throwing a 30007 error in Twilio
        #message = f'Job {job.purchase_order} has been ASSIGNED to you for tail number {job.tailNumber} to be completed before {complete_by}. Please go to you Livetakeoff App and check it out http://livetakeoff.com/jobs/{job.id}/details'

        # message needs to have the following format:
        #Job ASSIGNED to you
        #• MIA
        #• N1122AA
        #• Signature MIA
        # Where MIA is the airport initials
        # N1122AA is the tail number
        # Signature MIA is the job.fbo.name
        # 2/4/24 13:00 is the job.completeBy

        message = f'Job ASSIGNED to you\n• {job.airport.initials}\n• {job.tailNumber}\n• {job.fbo.name}\n'

        for phone_number in unique_phone_numbers:
            notification_util.send(message, phone_number.as_e164)

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


    