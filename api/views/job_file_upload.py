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
        access_level = request.data.get('access_level', 'is_admin_only')

        is_customer_uploaded = False
        is_customer_only = False
        is_public = False

        if request.user.profile.customer:
            is_customer_only = True
            is_customer_uploaded = True
        else:
            if access_level == 'is_customer_only':
                is_customer_only = True
            elif access_level == 'is_public':
                is_public = True

        p = JobFiles(job=job,
                    uploaded_by=request.user,
                    file=file,
                    name=file.name,
                    size=file.size,
                    is_public=is_public,
                    is_customer_only=is_customer_only,
                    customer_uploaded=is_customer_uploaded)
        
        p.save()

        serializer = JobFileSerializer(p)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
