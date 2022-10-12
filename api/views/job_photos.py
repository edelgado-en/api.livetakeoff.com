from django.db.models import Q
from rest_framework import (permissions, status)
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from rest_framework .response import Response

import cloudinary.uploader
import cloudinary

from ..models import JobPhotos

from ..serializers import JobPhotoSerializer

class JobPhotosView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobPhotoSerializer
    pagination_class = CustomPageNumberPagination
    lookup_url_kwarg = "jobid"

    def get_queryset(self):
        jobid = self.kwargs.get(self.lookup_url_kwarg)
        job_photos = JobPhotos.objects.filter(job=jobid)

        return job_photos

    def post(self, request, *args, **kwargs):
        jobid = self.kwargs.get(self.lookup_url_kwarg)
        for photo_id in request.data['photos']:
            # This is not deleting from cloudinary. It is only deleting from the database
            #job_photo = JobPhotos.objects.get(pk=photo_id)
            
            # This is not working
            #cloudinary.uploader.destroy('Screenshot_from_2022-09-04_11-47-11_zcocvu.png', invalidate=True)

            JobPhotos.objects.filter(pk=photo_id).delete()

        return Response(status.HTTP_200_OK)