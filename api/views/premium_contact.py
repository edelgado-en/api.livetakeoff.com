from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.email_util import EmailUtil

from api.models import (
    UserProfile
)

class PremiumContactView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def post(self, request):
        first_name = request.user.first_name
        last_name = request.user.last_name

        email = request.data.get('email')

        title = 'PREMIUM Membership Request'

        body = f'''
        <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Premium Membership Request</div>
        
        <div>
            <div style="padding:5px;font-weight: 700;">First Name</div>
            <div style="padding:5px">{first_name}</div>
            <div style="padding:5px;font-weight: 700;">Last Name</div>
            <div style="padding:5px">{last_name}</div>
            <div style="padding:5px;font-weight: 700;">Email</div>
            <div style="padding:5px">{email}</div>
        </div>
        '''

        email_util = EmailUtil()
        email_util.send_email('rob@cleantakeoff.com', title, body)

        return Response({'success': 'Email sent successfully'}, status=status.HTTP_200_OK)