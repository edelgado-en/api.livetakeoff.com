from django.contrib.auth.models import User
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Q

from api.email_util import EmailUtil


class ForgotPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)


    def post(self, request):
        email = request.data.get('email')
        userName = request.data.get('userName')

        if email:
            try:
                user = User.objects.filter(
                        Q(email__iexact=email),
                        Q(username__iexact=userName)
                    ).first()
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                reset_link = f"https://www.livetakeoff.com/shared/reset-password/{uid}/{token}"

                email_util = EmailUtil()

                body = f"""
                    <p>Hi there,</p>

                    <p>You recently requested to reset your password for your LiveTakeoff account. Click the button below to reset it:</p>

                    <p>
                    <a href="{reset_link}" style="
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #ef4444;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        font-weight: bold;
                    ">
                        Reset Password
                    </a>
                    </p>

                    <p>If the button above doesn't work, copy and paste this link into your browser:</p>

                    <p><a href="{reset_link}">{reset_link}</a></p>

                    <p>This link will expire shortly for your security.</p>

                    <p>If you didn't request a password reset, you can safely ignore this email.</p>

                    <p>Thanks,<br/>The LiveTakeoff Team</p>
                    """

                body += email_util.getEmailSignature()

                email_util.send_email(email, "Reset your password", body)

            except Exception as e:
                # Never reveal if email is invalid
                return Response({'error': 'Unable to send reset password email'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Email sent successfully'}, status=status.HTTP_200_OK)