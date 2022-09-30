from django.urls import path
from .views import (UserView, SendEmail)

urlpatterns = [
    path('users/me', UserView.as_view()),
    path('email/send', SendEmail.as_view()),
]