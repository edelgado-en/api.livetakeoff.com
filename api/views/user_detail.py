from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from api.serializers import UsersSerializer

from api.models import (UserEmail)


class UserDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        user = User.objects.select_related('profile').get(pk=id)

        emails = UserEmail.objects.filter(user=user)

        user.additional_emails = []

        if emails:
            email_array = []
            for email in emails:
                obj = {
                    'id': email.id,
                    'email': email.email
                }

                email_array.append(obj)

            user.additional_emails = email_array 

        serializer = UsersSerializer(user)
            
        return Response(serializer.data)
    

    def patch(self, request, id):
        user = User.objects.select_related('profile').get(pk=id)
        email = request.data.get('email', user.email)

        user.email = email
        user.save()

        user.additional_emails = []

        serializer = UsersSerializer(user)

        return Response(serializer.data, status.HTTP_200_OK)
