from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from api.email_util import EmailUtil

class UserSignupView(APIView):
    permission_classes = (AllowAny,)


    def post(self, request):

        # get all the fields from the request data
        first_name = request.data.get('firstName')
        last_name = request.data.get('lastName')
        email = request.data.get('email')
        phone_number = request.data.get('phoneNumber')
        role = request.data.get('selectedRole')
        vendor_name = request.data.get('vendorName')
        customer_name = request.data.get('customerName')

        if not vendor_name:
            vendor_name = 'Not specified'

        if not customer_name:
            customer_name = 'Not specified'

        subject = 'New User Signup Request'


        body = f'''
        <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">New User Signup Request</div>
        <table style="border-collapse: collapse">
            <tr>
                <td style="padding:15px">First Name</td>
                <td style="padding:15px">{first_name}</td>
            </tr>
            <tr>
                <td style="padding:15px">Last Name</td>
                <td style="padding:15px">{last_name}</td>
            </tr>
            <tr>
                <td style="padding:15px">Email</td>
                <td style="padding:15px">{email}</td>
            </tr>
            <tr>
                <td style="padding:15px">Phone Number</td>
                <td style="padding:15px">{phone_number}</td>
            </tr>
            <tr>
                <td style="padding:15px">Role</td>
                <td style="padding:15px">{role}</td>
            </tr>
            <tr>
                <td style="padding:15px">Vendor</td>
                <td style="padding:15px">{vendor_name}</td>
            </tr>
            <tr>
                <td style="padding:15px">Customer</td>
                <td style="padding:15px">{customer_name}</td>
            </tr>
        </table>
        '''

        email_util = EmailUtil()

        body += email_util.getEmailSignature()

        email_util.send_email('rob@cleantakeoff.com', subject, body)

        return Response({'success': 'Email sent successfully'}, status=status.HTTP_200_OK)
