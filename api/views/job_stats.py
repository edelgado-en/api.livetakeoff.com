from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import (permissions, status)
from rest_framework .response import Response

from ..models import (
        Job,
        JobComments,
        JobPhotos,
    )

class JobStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        comments_count = JobComments.objects.filter(job=job).count()
        photos_count = JobPhotos.objects.filter(job=job).count()

        response = {
            'comments_count': comments_count,
            'photos_count': photos_count
        }

        return Response(response, status=status.HTTP_200_OK)