from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.serializers import (JobPhotoSerializer, JobDetailSerializer, SharedJobDetailSerializer)

from api.models import (Job)


class SharedJobDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id):
        job = Job.objects \
                 .prefetch_related('photos') \
                 .prefetch_related('job_service_assignments') \
                 .prefetch_related('job_retainer_service_assignments') \
                 .get(pk=id)
        
        job_service_assignments = []
        job_retainer_service_assignments = []

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


        job.service_assignments = job_service_assignments
        job.retainer_service_assignments = job_retainer_service_assignments
        job.job_photos = job.photos.all()

        serializer = SharedJobDetailSerializer(job)

        return Response(serializer.data)