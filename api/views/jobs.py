from rest_framework import permissions
from rest_framework.generics import ListAPIView
from ..serializers.job import JobSerializer
from ..pagination import CustomPageNumberPagination
from ..models import Job

class JobListView(ListAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    #def get_queryset(self):
    #   return self.request.user.jobs.all()

