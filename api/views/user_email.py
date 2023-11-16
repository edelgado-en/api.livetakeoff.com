from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from api.models import (UserEmail)


class UserEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user_id = request.data.get('user_id', None)
        new_additional_email = request.data.get('new_additional_email', None)

        user = User.objects.get(id=user_id)

        # check that the email does not exist ignore case in user.email and user.additional_emails
        user_email = UserEmail.objects.filter(Q(user=user) & Q(email__iexact=new_additional_email)).first()

        if user_email:
            return Response({'error': 'A user with that email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check that the email does not exist ignore case in user.email
        user_email = User.objects.filter(email__iexact=new_additional_email).first()

        if user_email:
            return Response({'error': 'A user with that email already exists'}, status=status.HTTP_400_BAD_REQUEST)


        user_email = UserEmail.objects.create(user=user, email=new_additional_email)

        return Response({'id': user_email.id, 'email': user_email.email}, status=status.HTTP_200_OK)
    

    def patch(self, request, user_email_id):
        user_id = request.data.get('user_id', None)
        user = User.objects.get(pk=user_id)

        email = request.data.get('email', user.email)

        # fetch the user_email by user_email_id
        user_email = UserEmail.objects.get(pk=user_email_id)

        # check that the email does not exist ignore case in user.email and user.additional_emails
        user_email_check = UserEmail.objects.filter(Q(user=user) & Q(email__iexact=email)).first()

        if user_email_check:
            return Response({'error': 'A user with that email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check that the email does not exist ignore case in user.email
        user_email_check = User.objects.filter(email__iexact=email).first()

        if user_email_check:
            return Response({'error': 'A user with that email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_email.email = email

        user_email.save()

        return Response({'id': user_email.id, 'email': user_email.email}, status=status.HTTP_200_OK)
    
    
    def delete(self, request, user_email_id):
        user_email = UserEmail.objects.get(pk=user_email_id)

        user_email.delete()

        return Response({'id': user_email_id}, status=status.HTTP_200_OK)




