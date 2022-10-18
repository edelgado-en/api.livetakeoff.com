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
    EstimatedServiceTime)

from ..serializers import (
                    JobServiceAssignmentSerializer,
                    JobRetainerServiceAssignmentSerializer,
                    BasicUserSerializer
                )

class JobServiceAssignmentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):

        if not self.can_view_assignment_list(request.user):
           return Response({'error': 'You do not have permission to access this view'},
                            status=status.HTTP_403_FORBIDDEN)


        job = get_object_or_404(Job, pk=id)

        assignments = JobServiceAssignment \
                                .objects.select_related('service') \
                                .filter(job=job)

        retainer_assignments = JobRetainerServiceAssignment \
                                    .objects.select_related('retainer_service') \
                                    .filter(job=job)

        # Use a different serializer because you don't need the profile part
        service_assignments = JobServiceAssignmentSerializer(assignments, many=True)
        retainer_service_assignments = JobRetainerServiceAssignmentSerializer(retainer_assignments, many=True)


        # get project managers and their availability
        project_managers = User.objects.filter(groups__name='Project Managers')

        for project_manager in project_managers:
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
                estimated_time = EstimatedServiceTime.objects.get(service=assignment_in_process.service,
                                                                  aircraft_type=job_in_process.aircraftType)        

                if estimated_time is None:
                    continue

                print(latest_assignment_activity.timestamp)

            # Because you don't have estimated times, you are unavailable to calculate available soon
            # just say it is busy
            if total_estimated_work_hours == 0:
                project_manager.availability = 'busy'


            # OUTSIDE THE INNER LOOP I NEED TO KNOW: THIS PROJECT MANAGER HAS X HOURS OF WORK
            # NOW COMPARE NOW() VS X HOURS OF WORK AND IF THE DELTA IS LESS OR EQUAL THAN 1 HOUR
            # FLAG AS AVAILABLE SOON

            
            # TODO: YOU HAVE TO ALSO CHECK IN RETAINER SERVICES
            # you the aircraft type of the job and the service to check the estimated time


        users = BasicUserSerializer(project_managers, many=True)

        response = {
            'services': service_assignments.data,
            'retainer_services': retainer_service_assignments.data,
            'project_managers': users.data
        }

        return Response(response, status.HTTP_200_OK)


    def put(self, request, id):
        job = get_object_or_404(Job, pk=id)

        at_least_one_service_assigned = False

        # if all services are assigned and the job status is less than assigned, then set the job status to assigned
        for service in request.data['services']:
            
            assignment =  JobServiceAssignment.objects.get(pk=service['assignment_id'])
            
            if service['user_id']:
                user = User.objects.get(pk=service['user_id'])
                assignment.project_manager = user

                at_least_one_service_assigned = True

            else :
                assignment.project_manager = None

            assignment.save()


        # if there is at least one service assigned, then set the status to assigned
        current_status = job.status

        if at_least_one_service_assigned and (current_status == 'A' or current_status == 'U'):
            job.status = 'S' # assigned
            job.save()

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

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def can_view_assignment_list(self, user):
        if user.is_superuser \
           or user.is_staff \
           or user.groups.filter(name='Account Managers').exists():
           return True

        return False


    def can_view_assignment(self, user, job_service_assignment):
        if user.is_superuser \
           or user.is_staff \
           or user.groups.filter(name='Account Managers').exists():
           return True
           
        if job_service_assignment.project_manager.id == user.id:
            return True

        return False


    