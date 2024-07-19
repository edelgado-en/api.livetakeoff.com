import os
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from api.models import (JobFiles, Job)

from api.serializers import (JobFileSerializer)

class JobFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobFileSerializer
    lookup_url_kwarg = "jobid"

    def post(self, request, *args, **kwargs):
        jobid = self.kwargs.get(self.lookup_url_kwarg)
        job = get_object_or_404(Job, pk=jobid)
        file = request.data.get('file')
        is_public = request.data.get('is_public', False)

        if is_public == 'false':
            is_public = False
        else:
            is_public = True

        is_customer_uploaded = False

        if request.user.profile.customer:
            is_public = True
            is_customer_uploaded = True

        p = JobFiles(job=job,
                    uploaded_by=request.user,
                    file=file,
                    name=file.name,
                    size=file.size,
                    is_public=is_public,
                    customer_uploaded=is_customer_uploaded)
        
        p.save()

        serializer = JobFileSerializer(p)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
