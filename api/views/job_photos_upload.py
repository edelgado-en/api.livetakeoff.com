from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from datetime import datetime

from ..models import (
        JobPhotos,
        Job,
        JobServiceAssignment,
        JobRetainerServiceAssignment)
from ..serializers import JobPhotoSerializer

TOTAL_PHOTOS_MAX_COUNT = 20

class JobPhotosUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobPhotoSerializer
    lookup_url_kwarg = "jobid"

    def post(self, request, *args, **kwargs):
        jobid = self.kwargs.get(self.lookup_url_kwarg)
        job = get_object_or_404(Job, pk=jobid)

        if not self.can_view_job(request.user, job):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)
        
        is_interior = request.data['is_interior']
        interior = False
        if (is_interior == 'true'):
            interior = True

        total_photos = JobPhotos.objects.filter(job=jobid, interior=interior).count()

        if total_photos > TOTAL_PHOTOS_MAX_COUNT:
            return Response({'error': 'There is aleady 20 photos associated with this job'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        counter = 0

        name = job.tailNumber + '_' + job.airport.initials + '_' + datetime.today().strftime('%Y-%m-%d')

        for photo in request.data.getlist('photo'):
            name = name + '_' + str(counter)
            
            p = JobPhotos(job=job,
                          uploaded_by=request.user,
                          image=photo,
                          name=name,
                          size=photo.size,
                          interior=interior)
            p.save()
            
            counter = counter + 1

        return Response({'uploaded_photos': counter}, status=status.HTTP_201_CREATED)


    def can_view_job(self, user, job):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
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
