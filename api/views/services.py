from rest_framework import (permissions, status)

from ..serializers import (ServiceSerializer)
from rest_framework.generics import ListCreateAPIView
from ..models import (Service)

class ServicesView(ListCreateAPIView):
    queryset = Service.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ServiceSerializer

    def get_queryset(self):
        name = self.request.data.get('name', '')

        qs = Service.objects \
                       .filter(active=True) \
                       .order_by('name')
        
        if name:
            qs = qs.filter(name__icontains=name)

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)