from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from api.serializers import (
        HelpFileSerializer,
    )

from ..pagination import CustomPageNumberPagination
from api.models import (
        Help
    )

class HelpFileListView(ListAPIView):
    serializer_class = HelpFileSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        search_text = self.request.data.get('searchText', '')

        qs = Help.objects \
                        .filter(Q(name__icontains=search_text)) \
                        .order_by('-created_at')
        
        if self.request.user.groups.filter(name='Internal Coordinators').exists():
            if self.request.user.groups.filter(name='Project Managers').exists():
                qs = qs.filter(Q(access_level='I') | Q(access_level='P') | Q(access_level='A'))
            else:
                qs = qs.filter(Q(access_level='I') | Q(access_level='A'))

        elif self.request.user.groups.filter(name='Project Managers').exists():
            if self.request.user.profile.vendor and self.request.user.profile.vendor.is_external:
                qs = qs.filter(Q(access_level='E') | Q(access_level='A'))
            else:
                qs = qs.filter(Q(access_level='P') | Q(access_level='A'))

        elif self.request.user.profile.customer:
            qs = qs.filter(Q(access_level='C'))
        
        elif self.request.user.is_superuser \
          or self.request.user.is_staff \
          or self.request.user.groups.filter(name='Account Managers').exists():
            qs = qs.filter(Q(access_level='I') | Q(access_level='P') | Q(access_level='E') | Q(access_level='C') | Q(access_level='A'))

        return qs
    

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

