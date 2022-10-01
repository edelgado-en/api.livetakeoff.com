from rest_framework import permissions
from django.contrib.auth.models import User
from .models.job_photo import JobPhotos
from rest_framework.response import Response
from rest_framework.views import APIView
import os
from django.core.mail import send_mail, mail_admins, BadHeaderError
from templated_mail.mail import BaseEmailMessage
from twilio.rest import Client 

class UserView(APIView):

    def get(self, request):
        photos = JobPhotos.objects.all()

        for photo in photos:
            print(photo.image.url)

        return Response('hello')

class SendEmail(APIView):

    def get(self, request):

        #This is working in the sandbox
        """ account_sid = os.environ.get('TWILIO_ACCOUNT_SID') 
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token) 
 
        message = client.messages.create( 
                              from_='whatsapp:+14155238886',  
                              body='testing message',      
                              to='whatsapp:+19542133394' 
                          ) 
 
        print(message.sid) """

        # I need to disconnect from VPN for this to work
        """ try:
            message = BaseEmailMessage(
                template_name='emails/customer.html',
                context={'name': 'Enrique'}
            )

            message.send(['enriquedelgado806@gmail.com'])

        except BadHeaderError as e:
            print(e) """


        return Response('hello from send email')
