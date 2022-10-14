from django.urls import path
from .views import (
        JobListView,
        UserView,
        JobDetail,
        JobServiceAssignmentView,
        JobRetainerServiceAssignmentView,
        JobPhotosView,
        JobPhotosUploadView,
        UserAvatarView,
        UserResetPasswordView,
        JobCommentView,
        JobStatsView,
        JobFormInfoView
    )

urlpatterns = [
    path('jobs', JobListView.as_view()),
    path('jobs/form-info', JobFormInfoView.as_view()),
    path('jobs/<int:id>/', JobDetail.as_view()),
    path('jobs/stats/<int:id>/', JobStatsView.as_view()),
    path('jobs/services/<int:id>/', JobServiceAssignmentView.as_view()),
    path('jobs/retainer-services/<int:id>/', JobRetainerServiceAssignmentView.as_view()),
    path('job-photos/<int:jobid>/', JobPhotosView.as_view()),
    path('job-photos/delete/<int:jobid>/', JobPhotosView.as_view()),
    path('job-photos/upload/<int:jobid>/', JobPhotosUploadView.as_view()),
    path('job-comments/<int:jobid>/', JobCommentView.as_view()),
    path('users/me', UserView.as_view()),
    path('users/me/avatar', UserAvatarView.as_view()),
    path('users/me/reset-password', UserResetPasswordView.as_view())
]