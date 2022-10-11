from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

class UserResetPasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request):
        user = get_object_or_404(User, pk=request.user.id)

        new_password = request.data['new_password']
        new_password_again = request.data['new_password_again']

        if new_password != new_password_again:
            return Response(status.HTTP_406_NOT_ACCEPTABLE)

        user.set_password(new_password)

        user.save()

        return Response(status.HTTP_200_OK)