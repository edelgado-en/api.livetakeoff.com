from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from api.models import (
        JobRetainerServiceAssignment,
        JobServiceAssignment,
        Job,
        RetainerService,
        RetainerServiceActivity,
        JobStatusActivity
    )

from api.serializers import JobRetainerServiceAssignmentSerializer

class JobRetainerServiceAssignmentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        """ 
        Completes assignment
        """
        job_retainer_service_assignment = get_object_or_404(JobRetainerServiceAssignment, pk=id)

        if not self.can_view_assignment(request.user, job_retainer_service_assignment):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobRetainerServiceAssignmentSerializer(job_retainer_service_assignment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            #save retainer service activity
            RetainerServiceActivity.objects.create(job=job_retainer_service_assignment.job,
                                                   retainer_service=job_retainer_service_assignment.retainer_service,
                                                   project_manager=request.user,
                                                   status='C')


            # if all services and retainer services associated with this job are completed, then this job is a candidate to be completed
            # return a boolean to the front end to indicate if the job can be completed
            job = job_retainer_service_assignment.job
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


    def post(self, request, id):
        job = get_object_or_404(Job, pk=id)
        retainer_service = get_object_or_404(RetainerService, pk=request.data['retainer_service_id'])

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
                RetainerServiceActivity.objects.create(job=job,
                                                   retainer_service=retainer_service,
                                                   project_manager=project_manager,
                                                   status='C')

        retainer_assignment = JobRetainerServiceAssignment(job=job,
                                                           project_manager=project_manager,
                                                           retainer_service=retainer_service,
                                                           status=status)
        retainer_assignment.save()

        #Create JobStatusActivity for the retainer service assignment
        JobStatusActivity.objects.create(job=job,
                                        status=status,
                                        user=request.user,
                                        activity_type='X',
                                        service_name=retainer_service.name)

        updated_job = Job.objects.get(pk=job.id)

        if job.status != 'I':
            external_vendor = None
            for service_assignment in updated_job.job_retainer_service_assignments.all():
                if service_assignment.vendor:
                    external_vendor = service_assignment.vendor
            
            updated_job.vendor = external_vendor

            # adjust the subcontractor_profit if there is a external_vendor
            if external_vendor:
                vendor_charge = updated_job.vendor_charge if updated_job.vendor_charge else 0
                vendor_additional_cost = updated_job.vendor_additional_cost if updated_job.vendor_additional_cost else 0
                updated_job.subcontractor_profit = updated_job.price - (vendor_charge + vendor_additional_cost)

            updated_job.save()

        serializer = JobRetainerServiceAssignmentSerializer(retainer_assignment)

        return Response(serializer.data)   

    
    def delete(self, request, id):
        job_retainer_service_assignment = get_object_or_404(JobRetainerServiceAssignment, pk=id)

        # get job before deleting service
        job_id = job_retainer_service_assignment.job.id

        # Create JobStatusActivity for the retainer service removed
        JobStatusActivity.objects.create(job=job_retainer_service_assignment.job,
                                        status=job_retainer_service_assignment.status,
                                        user=request.user,
                                        activity_type='Y',
                                        service_name=job_retainer_service_assignment.retainer_service.name)

        # delete the service activities associated with this service
        RetainerServiceActivity.objects.filter(job=job_id, retainer_service=job_retainer_service_assignment.retainer_service).delete()

        job_retainer_service_assignment.delete()

        # fetch job and update price after deleting service
        job = Job.objects.get(pk=job_id)

        external_vendor = None

        for service_assignment in job.job_retainer_service_assignments.all():
            if service_assignment.vendor:
                external_vendor = service_assignment.vendor

        job.vendor = external_vendor
        job.save()

        return Response({'message': 'Delete successfully'}, status.HTTP_200_OK)



    def can_view_assignment(self, user, job_retainer_service_assignment):
        if user.is_superuser \
           or user.is_staff \
           or user.groups.filter(name='Internal Coordinators').exists() \
           or user.groups.filter(name='Account Managers').exists():
           return True
           
        if job_retainer_service_assignment.project_manager.id == user.id:
            return True

        return False