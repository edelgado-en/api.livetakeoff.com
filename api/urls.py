from django.urls import path
from .views import (
        JobListView,
        UserView,
        JobDetail,
        JobServiceAssignmentView,
        JobRetainerServiceAssignmentView
    )

urlpatterns = [
    path('jobs', JobListView.as_view()),
    path('jobs/<int:id>/', JobDetail.as_view()),
    path('jobs/services/<int:id>/', JobServiceAssignmentView.as_view()),
    path('jobs/retainer-services/<int:id>/', JobRetainerServiceAssignmentView.as_view()),
    path('users/me', UserView.as_view()),
]