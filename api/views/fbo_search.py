from django.db.models import Q
from rest_framework import (permissions, status)

from ..serializers import (FBOSerializer)
from rest_framework.generics import ListAPIView
from ..models import FBO

class FboSearchView(ListAPIView):
    queryset = FBO.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FBOSerializer

    def get_queryset(self):
        name = self.request.data.get('name', '')

        qs = FBO.objects \
                       .filter(name__icontains=name, active=True) \
                       .order_by('name')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)