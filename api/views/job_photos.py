from django.db.models import Q
from rest_framework import (permissions, status)
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from rest_framework .response import Response

import cloudinary.uploader
import cloudinary

from api.models import (JobPhotos, Job)

from ..serializers import JobPhotoSerializer

class JobPhotosView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobPhotoSerializer
    pagination_class = CustomPageNumberPagination
    lookup_url_kwarg = "jobid"


    def get(self, request, *args, **kwargs):
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        if not self.can_view_photos(self.request.user, job):
            return Response({'error': 'You do not have permission to view photos for this job'}, status=status.HTTP_403_FORBIDDEN)

        return self.list(request, *args, **kwargs)


    def get_queryset(self):
        jobid = self.kwargs.get(self.lookup_url_kwarg)
        job_photos = JobPhotos.objects.filter(job=jobid)

        return job_photos


    def post(self, request, *args, **kwargs):
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        if not self.can_view_photos(self.request.user, job):
            return Response({'error': 'You do not have permission to delete photos for this job'}, status=status.HTTP_403_FORBIDDEN)


        for photo_id in request.data['photos']:
            # This is not deleting from cloudinary. It is only deleting from the database
            job_photo = JobPhotos.objects.get(pk=photo_id)
            
            # this deletes from cloudinary!
            job_photo.image.delete()
            
            # now delete the instance from the database
            JobPhotos.objects.filter(pk=photo_id).delete()

        return Response(status.HTTP_200_OK)


    def can_view_photos(self, user, job):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Project Managers').exists() \
          or user.groups.filter(name='Account Managers').exists():
           return True

        if user.profile.customer and user.profile.customer == job.customer:
            return True


        return False