from django.urls import path
from .views import UserView

urlpatterns = [
    path('users/me', UserView.as_view()),
]