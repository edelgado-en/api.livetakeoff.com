from django.urls import path
from .views import (JobListView, UserView, JobDetail)

urlpatterns = [
    path('jobs', JobListView.as_view()),
    path('jobs/<int:id>/', JobDetail.as_view()),
    path('users/me', UserView.as_view()),
]