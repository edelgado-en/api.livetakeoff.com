from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..serializers import (JobCommentSerializer)
from ..models import (JobComments, Job)

class JobCommentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    lookup_url_kwarg = "jobid"

    def get(self, request):
        job = Job.objects.get(pk=self.lookup_url_kwarg)

        comments = JobComments.objects.filter(job=job)

        serializer = JobCommentSerializer(comments, many=True)

        return Response(serializer.data)