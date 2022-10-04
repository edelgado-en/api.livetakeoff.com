from django.urls import path
from .views import (JobListView, UserView)

urlpatterns = [
    path('jobs', JobListView.as_view()),
    path('users/me', UserView.as_view()),
]