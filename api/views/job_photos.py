from django.db.models import Q
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination

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