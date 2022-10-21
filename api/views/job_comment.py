from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

from ..serializers import (JobCommentSerializer)
from rest_framework.generics import ListCreateAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (JobComments, Job, JobCommentCheck)


class JobCommentView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobCommentSerializer
    pagination_class = CustomPageNumberPagination
    lookup_url_kwarg = "jobid"

    def get_queryset(self):
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        now = datetime.now()

        try:
            job_comment_check = JobCommentCheck.objects.get(job=job, user=self.request.user)
            job_comment_check.last_time_check = now
            job_comment_check.save()

        except JobCommentCheck.DoesNotExist:
            job_comment_check = JobCommentCheck(job=job, user=self.request.user, last_time_check=now)
            job_comment_check.save()

        return JobComments.objects.select_related('author').filter(job=job).order_by('created')

    def create(self, request, *args, **kwargs):
        user = self.request.user
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        comment = self.request.data['comment']

        job_comment = JobComments(job=job,
                                  comment=comment,
                                  author=user)

        job_comment.save()

        serializer = JobCommentSerializer(job_comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)



