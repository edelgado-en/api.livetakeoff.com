from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from api.models import Job
from ..serializers import (
        JobAdminSerializer
    )


class CompletedJobsListView(ListAPIView):
    serializer_class = JobAdminSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        
        qs = Job.objects.prefetch_related('job_service_assignments') \
                          .prefetch_related('job_retainer_service_assignments') \
                          .filter(Q(status='C') | Q(status='I') | Q(status='T')) \
                          .order_by('status') \
                          .all()

        return qs


    def post(self, request, *args, **kwargs):
        if not self.can_see_completed_list(request.user):
            return Response({'error': 'You do not have permission to view completed jobs'}, status=status.HTTP_403_FORBIDDEN)


        return self.list(request, *args, **kwargs)


    def patch(self, request, *args, **kwargs):
        if not self.can_see_completed_list(request.user):
            return Response({'error': 'You do not have permission to edit completed jobs'}, status=status.HTTP_403_FORBIDDEN)

        job = get_object_or_404(Job, pk=kwargs['id'])

        serializer = JobAdminSerializer(job, data=request.data, partial=True)

        # TODO: handle invoice processing

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status.HTTP_200_OK)
        
        return Response({'error': 'Missing Required Fields'}, status.HTTP_400_BAD_REQUEST)


    def can_see_completed_list(self, user):
        return user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists()