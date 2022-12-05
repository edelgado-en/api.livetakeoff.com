import os
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
        JobStatusActivity,
        JobRetainerServiceAssignment)
from ..serializers import JobPhotoSerializer

TOTAL_PHOTOS_MAX_COUNT = 10

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

        total_photos = JobPhotos.objects.filter(job=jobid, interior=interior, customer_uploaded=False).count()

        # check if the total photos plus the new ones is greater than the max
        if total_photos + len(request.data.getlist('photo')) > TOTAL_PHOTOS_MAX_COUNT:
            return Response({'error': 'There is aleady 10 photos associated with this job'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        counter = 0

        name = job.tailNumber + '_' + job.airport.initials + '_' + datetime.today().strftime('%Y-%m-%d')

        for photo in request.data.getlist('photo'):
            file_name, file_extension = os.path.splitext(photo.name)
            
            filename = name + '_' + str(counter) + file_extension

            photo._name = filename
            
            p = JobPhotos(job=job,
                          uploaded_by=request.user,
                          image=photo,
                          name=filename,
                          size=photo.size,
                          interior=interior)
            p.save()

            counter = counter + 1


        JobStatusActivity.objects.create(job=job, user=request.user,
                                    status=job.status, activity_type='U')


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
