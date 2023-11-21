from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from api.serializers import (
     JobFileSerializer,
)

from api.models import (
        JobFiles
    )

class JobFileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        job_file = get_object_or_404(JobFiles, pk=id)
        
        is_public = request.data.get('is_public', None)

        if is_public is not None:
            job_file.is_public = is_public
            job_file.save()

        serializer = JobFileSerializer(job_file)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def delete(self, request, id):
        job_file = get_object_or_404(JobFiles, pk=id)
        job_file.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)