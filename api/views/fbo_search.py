from django.db.models import Q, F
from rest_framework import (permissions, status)

from ..serializers import (FBOSerializer)
from rest_framework.generics import ListAPIView
from ..models import FBO
from ..pagination import CustomPageNumberPagination

class FboSearchView(ListAPIView):
    queryset = FBO.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FBOSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        name = self.request.data.get('name', '')
        airport_id = self.request.data.get('airport_id', None)
        sort_selected = self.request.data.get('sortSelected', None)

        qs = FBO.objects \
                       .filter(name__icontains=name, active=True)
        
        if airport_id:
            qs = qs.filter(available_airports__airport_id=airport_id).distinct()

        if sort_selected:
            # sort_selected can be either 'asc' or 'desc'
            # sort by airport.fee
            if sort_selected == 'asc':
                # nulls should be first, then order by fee asc
                qs = qs.order_by(F('fee').asc(nulls_first=True))

            elif sort_selected == 'desc':
                qs = qs.order_by(F('fee').desc(nulls_last=True))

        else:
            qs = qs.order_by('name')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)