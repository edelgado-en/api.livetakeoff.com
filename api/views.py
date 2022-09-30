from rest_framework import permissions
from django.contrib.auth.models import User
from .models import JobPhotos
from rest_framework.response import Response
from rest_framework.views import APIView
import os
from django.core.mail import send_mail, mail_admins, BadHeaderError
from templated_mail.mail import BaseEmailMessage

class UserView(APIView):

    def get(self, request):
        photos = JobPhotos.objects.all()

        for photo in photos:
            print(photo.image.url)

        return Response('hello')

class SendEmail(APIView):

    #This is working
    def get(self, request):
        try:
            message = BaseEmailMessage(
                template_name='emails/customer.html',
                context={'name': 'Enrique'}
            )

            message.send(['enriquedelgado806@gmail.com'])

        except BadHeaderError as e:
            print(e)

        return Response('hello from send email')
