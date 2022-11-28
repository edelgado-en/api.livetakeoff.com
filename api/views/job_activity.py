from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import User

from api.models import (Job, JobStatusActivity)

from api.serializers import JobActivitySerializer

class JobActivityView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobActivitySerializer
    lookup_url_kwarg = "jobid"


    def get_queryset(self):
        jobid = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=jobid)

        # if the current user is a customer, exclude job status activities related to price changed
        if self.request.user.profile.customer and self.request.user.profile.customer == job.customer:
            return JobStatusActivity.objects.filter(job=job).exclude(Q(status='P')).order_by('timestamp')

        if  not self.request.user.profile.customer:
            return JobStatusActivity.objects.filter(job=jobid).order_by('timestamp')

        return Response({'error': 'You do not have permission to view job activity for this job'}, status=status.HTTP_403_FORBIDDEN)



