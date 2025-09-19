from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

from api.email_notification_service import EmailNotificationService

from api.models import (
    JobFeedback,
    Job
)

from api.serializers import JobFeedbackSerializer

class JobFeedbackView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobFeedbackSerializer

    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        feedbacks = JobFeedback.objects.filter(job=job). order_by('created')
        serializer = JobFeedbackSerializer(feedbacks, many=True)

        return Response(serializer.data)


    def post(self, request):
        job_id = request.data.get('job_id')
        rating = request.data.get('rating', 0)
        comment = request.data.get('comment', '')

        if not job_id:
            return Response({'detail': 'job_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        if rating < 1 or rating > 5:
            return Response({'detail': 'rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)

        job = get_object_or_404(Job, pk=job_id)

        job.feedback_rating = rating
        job.feedback_author = request.user
        job.save()

        if comment:
            feedback = JobFeedback(
                job=job,
                comment=comment,
                author=request.user,
                created=datetime.now()
            )

            feedback.save()

        EmailNotificationService().send_job_feedback_notification(job, comment)

        return Response({'detail': 'Feedback submitted successfully'}, status=status.HTTP_200_OK)

        