from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

import base64

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
            # if customer user then only include public comments
            
            qs = JobComments.objects.filter(job=job,
                                            created__gt=job_comment_check.last_time_check) \
                                            .exclude(author=request.user)

            # if customer user and customer matches job customer then only return public comments
            # request.user.profile.customer and request.user.profile.customer == job.customer
            if request.user.profile.customer and request.user.profile.customer == job.customer:
                qs = qs.filter(is_public=True)

            comments_count = qs.count()
                                                

        except JobCommentCheck.DoesNotExist:
            # this means that the user hasn't check the comments section for this job
            qs = JobComments.objects.filter(job=job).exclude(author=request.user)

            if request.user.profile.customer and request.user.profile.customer == job.customer:
                qs = qs.filter(is_public=True)

            comments_count = qs.count()


        photos_count = JobPhotos.objects.filter(job=job).count()

        message = str(job.id) + '-' + job.tailNumber
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        encoded_id = base64_bytes.decode('ascii')


        response = {
            'purchase_order': job.purchase_order,
            'comments_count': comments_count,
            'photos_count': photos_count,
            'encoded_id': encoded_id
        }

        return Response(response, status=status.HTTP_200_OK)