from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.email_util import EmailUtil

class ContactView(APIView):
    permission_classes = (permissions.AllowAny,)


    def post(self, request):
        first_name = request.data.get('firstName')
        last_name = request.data.get('lastName')
        email = request.data.get('email')
        phone = request.data.get('phone')
        subject = request.data.get('subject')
        message = request.data.get('message')

        if not phone:
            phone = 'Not specified'

        title = 'User Contact Us Request'

        body = f'''
        <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">User Contact Us Request</div>
        
        <div>
            <div style="padding:5px;font-weight: 700;">First Name</div>
            <div style="padding:5px">{first_name}</div>
            <div style="padding:5px;font-weight: 700;">Last Name</div>
            <div style="padding:5px">{last_name}</div>
            <div style="padding:5px;font-weight: 700;">Email</div>
            <div style="padding:5px">{email}</div>
            <div style="padding:5px;font-weight: 700;">Phone Number</div>
            <div style="padding:5px">{phone}</div>
            <div style="padding:5px;font-weight: 700;">Subject</div>
            <div style="padding:5px">{subject}</div>
            <div style="padding:5px;font-weight: 700;">Message</div>
            <div style="padding:5px">{message}</div>
        </div>
        '''
        email_util = EmailUtil()

        body += email_util.getEmailSignature()

        email_util.send_email('rob@cleantakeoff.com', title, body)

        return Response({'success': 'Email sent successfully'}, status=status.HTTP_200_OK)