from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from datetime import datetime

from ..serializers import (ServiceSerializer)
from rest_framework.generics import ListCreateAPIView
from ..models import (Service)

class ServicesView(ListCreateAPIView):
    queryset = Service.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ServiceSerializer