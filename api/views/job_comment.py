from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..serializers import (JobCommentSerializer)
from rest_framework.generics import ListCreateAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (JobComments, Job)


class JobCommentView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobCommentSerializer
    pagination_class = CustomPageNumberPagination
    lookup_url_kwarg = "jobid"

    def get_queryset(self):
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)
        
        return JobComments.objects.select_related('author').filter(job=job)


    def perform_create(self, serializer):
        user = self.request.user
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        comment = self.request.data['comment']

        job_comment = JobComments(job=job,
                                  comment=comment,
                                  author=user)

        job_comment.save()

