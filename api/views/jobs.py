from django.db.models import Q
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from ..serializers.job import JobSerializer
from ..pagination import CustomPageNumberPagination
from ..models import (
        Job,
        JobServiceAssignment,
        JobRetainerServiceAssignment
    )

class JobListView(ListAPIView):
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        if self.request.user.is_superuser \
          or self.request.user.is_staff \
          or self.request.user.groups.filter(name='Account Managers').exists():
           return Job.objects.filter(~Q(status='I')).order_by('-completeBy').all()

        # You are a Project Manager

        job_ids = set()

        # Get job ids from pending services/retainer_services assigned to the current user
        # If you have at least one pending service assigned to you, you can see the job
        assignments = JobServiceAssignment.objects.filter(project_manager=self.request.user.id).all()

        for assignment in assignments:
            if assignment.status != 'C':
                job_ids.add(assignment.job.id)
        
        retainer_assignment = JobRetainerServiceAssignment.objects.filter(project_manager=self.request.user.id).all()

        for assignment in retainer_assignment:
            if assignment.status != 'C':
                job_ids.add(assignment.job.id)

        return Job.objects \
                  .filter(~Q(status='I')) \
                  .filter(id__in=job_ids) \
                  .order_by('-completeBy') \
                  .all()



