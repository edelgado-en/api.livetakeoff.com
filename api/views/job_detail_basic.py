from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..serializers import (
     JobDetailBasicSerializer,
     )

from ..models import (
        Job,
    )


class JobDetailBasicView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)
        serializer = JobDetailBasicSerializer(job)

        return Response(serializer.data)


