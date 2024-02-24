from rest_framework import (permissions, status)

from ..serializers import (RetainerServiceSerializer)
from rest_framework.generics import ListCreateAPIView
from api.models import (RetainerService)


class RetainerServicesView(ListCreateAPIView):
    queryset = RetainerService.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RetainerServiceSerializer

    def get_queryset(self):
        name = self.request.data.get('name', '')

        qs = RetainerService.objects \
                       .filter(active=True) \
                       .order_by('name')
        
        if name:
            qs = qs.filter(name__icontains=name)

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)