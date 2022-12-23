from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.email_util import EmailUtil


class ForgotPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)


    def post(self, request):
        userName = request.data.get('userName')
        email = request.data.get('email')

        title = 'Forgot Password Request'

        body = f'''
        <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Forgot Password Request</div>
        
        <div style="font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 20px; color: red">***For security reasons, ENSURE the email provided matches the email for the username provided, Otherwise, do NOT reset the password.***</div>

        <div>
            <div style="padding:5px;font-weight: 700;">UserName</div>
            <div style="padding:5px">{userName}</div>
            <div style="padding:5px;font-weight: 700;">Email</div>
            <div style="padding:5px">{email}</div>
        </div>
        '''

        email_util = EmailUtil()
        email_util.send_email('rob@cleantakeoff.com', title, body)

        return Response({'success': 'Email sent successfully'}, status=status.HTTP_200_OK)