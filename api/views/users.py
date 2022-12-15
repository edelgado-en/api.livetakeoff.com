from django.db.models import Q
from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from ..pagination import CustomPageNumberPagination

from api.serializers import UsersSerializer

class UsersView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination
    serializer_class = UsersSerializer

    def get_queryset(self):
        name = self.request.data.get('name')

        users = User.objects.filter(Q(username__icontains=name)
                                     | Q(first_name__icontains=name)
                                     | Q(last_name__icontains=name)) \
                            .filter(is_active=True) \
                            .select_related('profile') \
                            .order_by('first_name', 'last_name')

        return users


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)