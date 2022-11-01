from django.db.models import Q
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from ..serializers import (
        JobSerializer,
        JobAdminSerializer
    )

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

    # TODO: you have to get a different jobserializer for Account Managers/Admin/SuperUsers
    # in that serializer you have to also get customer and assignees
    def get_serializer_class(self):
        if self.request.user.is_superuser \
          or self.request.user.is_staff \
          or self.request.user.groups.filter(name='Account Managers').exists():
            return JobAdminSerializer

        return JobSerializer


    def get_queryset(self):
        if self.request.user.is_superuser \
          or self.request.user.is_staff \
          or self.request.user.groups.filter(name='Account Managers').exists():

            searchText = self.request.data['searchText']
            status = self.request.data['status']

            qs = Job.objects.prefetch_related('job_service_assignments') \
                             .prefetch_related('job_retainer_service_assignments') \
                             .select_related('customer') \
                             .select_related('aircraftType')\
                             .select_related('airport') \
                             .select_related('fbo') \
                             .order_by('completeBy') \
                             .all()

            if searchText:
                qs = qs.filter(Q(tailNumber__icontains=searchText)
                               | Q(customer__name__icontains=searchText)
                               | Q(purchase_order__icontains=searchText)
                               | Q(airport__initials__icontains=searchText)
                              )

            if status == 'All':
                qs = qs.filter(Q(status='A') | Q(status='S') | Q(status='U') | Q(status='W') | Q(status='R'))
            else:
                qs = qs.filter(status=status)

            return qs

        # You are a Project Manager

        job_ids = set()

        # Get job ids from pending services/retainer_services assigned to the current user
        # If you have at least one pending service assigned to you, you can see the job
        assignments = JobServiceAssignment.objects \
                                          .select_related('job') \
                                          .filter(project_manager=self.request.user.id) \
                                          .all()

        for assignment in assignments:
            if assignment.status != 'C':
                job_ids.add(assignment.job.id)
        
        retainer_assignment = JobRetainerServiceAssignment.objects \
                                                          .select_related('job') \
                                                          .filter(project_manager=self.request.user.id) \
                                                          .all()

        for assignment in retainer_assignment:
            if assignment.status != 'C':
                job_ids.add(assignment.job.id)

        # the only statuses that a PM can see is Assigned and WIP
        return Job.objects \
                  .filter(Q(status='S') | Q(status='W')) \
                  .filter(id__in=job_ids) \
                  .order_by('completeBy') \
                  .all()


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

