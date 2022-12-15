from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from api.serializers import UsersSerializer


class UserDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        user = User.objects.select_related('profile').get(pk=id)

        serializer = UsersSerializer(user)
            
        return Response(serializer.data)