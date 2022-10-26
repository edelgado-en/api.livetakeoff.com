from django.db.models import Q
from rest_framework import (permissions, status)

from ..serializers import (BasicUserSerializer)
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import User


class CustomerUsersView(ListAPIView):
    queryset = User.objects.select_related('profile').filter(profile__customer__isnull=False)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BasicUserSerializer