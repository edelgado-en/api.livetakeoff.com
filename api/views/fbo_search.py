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
        airport_id = self.request.data.get('airport_id', None)

        qs = FBO.objects \
                       .filter(name__icontains=name, active=True) \
                       .order_by('name')
        
        if airport_id:
            qs = qs.filter(available_airports__airport_id=airport_id).distinct()

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)