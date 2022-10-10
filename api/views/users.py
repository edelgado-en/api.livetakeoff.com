from rest_framework import permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import UserProfile

class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user)

        avatar = None

        if user_profile and user_profile.avatar:
            avatar = user_profile.avatar.url

        first_name = ''
        last_name = ''

        if not user.first_name:
            first_name = user.username
        else:
            first_name = user.first_name

        if not user.last_name:
            last_name = user.username
        else:
            last_name = user.last_name

        content = {
            "initials": first_name[0] + last_name[0],
            "about": user_profile.about,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "isProjectManager": user.groups.filter(name='Project Managers').exists(),
            "AccountManager": user.groups.filter(name='Account Managers').exists(),
            "isAdmin": user.is_staff,
            "isSuperUser": user.is_superuser,
            "fullName": first_name + ' ' + last_name,
            "avatar": avatar
        }

        return Response(content)