from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.contrib.auth.models import User

from ..models import UserProfile

class UserAvatarView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user)

        avatar = request.data['avatar']

        user_profile.avatar = avatar

        user_profile.save()

        content = {
            'avatar': user_profile.avatar.url
        }

        return Response(content, status.HTTP_200_OK);