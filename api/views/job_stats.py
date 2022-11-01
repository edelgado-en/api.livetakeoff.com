from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

from ..models import (
        Job,
        JobComments,
        JobPhotos,
        JobCommentCheck
    )

class JobStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        comments_count = 0

        try:
            job_comment_check = JobCommentCheck.objects.get(job=job, user=request.user)

            # Only show me the comments that have been created AFTER job_comments_check.last_time_check
            comments_count = JobComments.objects.filter(
                                                    job=job,
                                                    created__gt=job_comment_check.last_time_check) \
                                                .exclude(author=request.user) \
                                                .count()

        except JobCommentCheck.DoesNotExist:
            # this means that the user hasn't check the comments section for this job
            comments_count = JobComments.objects.filter(job=job).exclude(author=request.user).count()

        photos_count = JobPhotos.objects.filter(job=job).count()

        response = {
            'purchase_order': job.purchase_order,
            'comments_count': comments_count,
            'photos_count': photos_count
        }

        return Response(response, status=status.HTTP_200_OK)