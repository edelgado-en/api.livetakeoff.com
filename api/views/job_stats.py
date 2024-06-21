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

        photos_count = JobPhotos.objects.filter(job=job).count()

        message = str(job.id) + '-' + job.tailNumber
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        encoded_id = base64_bytes.decode('ascii')


        response = {
            'purchase_order': job.purchase_order,
            'photos_count': photos_count,
            'encoded_id': encoded_id
        }

        return Response(response, status=status.HTTP_200_OK)