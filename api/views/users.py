from rest_framework import permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        
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
            "isProjectManager": user.groups.filter(name='Project Managers').exists(),
            "AccountManager": user.groups.filter(name='Account Managers').exists(),
            "isAdmin": user.is_staff,
            "isSuperUser": user.is_superuser,
            "fullName": first_name + ' ' + last_name,
        }

        return Response(content)