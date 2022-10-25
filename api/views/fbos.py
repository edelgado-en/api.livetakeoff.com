from django.db.models import Q
from rest_framework import (permissions, status)

from ..serializers import (FBOSerializer)
from rest_framework.generics import ListCreateAPIView
from ..models import (FBO)


class FBOsView(ListCreateAPIView):
    queryset = FBO.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FBOSerializer