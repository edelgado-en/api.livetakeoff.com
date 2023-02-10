from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
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


    def get_serializer_class(self):
        if self.request.user.is_superuser \
          or self.request.user.is_staff \
          or self.request.user.groups.filter(name='Account Managers').exists() \
          or self.request.user.groups.filter(name='Internal Coordinators').exists():
            return JobAdminSerializer

        return JobSerializer


    def get_queryset(self):
        if self.request.user.is_superuser \
          or self.request.user.is_staff \
          or self.request.user.groups.filter(name='Account Managers').exists() \
          or self.request.user.groups.filter(name='Internal Coordinators').exists():

            searchText = self.request.data['searchText']
            status = self.request.data['status']
            customer = self.request.data.get('customer')
            airport = self.request.data.get('airport')

            qs = Job.objects.prefetch_related('job_service_assignments') \
                             .prefetch_related('job_retainer_service_assignments') \
                             .prefetch_related('tags') \
                             .select_related('customer') \
                             .select_related('aircraftType')\
                             .select_related('airport') \
                             .select_related('fbo') \
                             .all()

            if searchText:
                qs = qs.filter(Q(tailNumber__icontains=searchText)
                               | Q(purchase_order__icontains=searchText)
                              )

            if status == 'All':
                qs = qs.filter(Q(status='A') | Q(status='S') | Q(status='U') | Q(status='W') | Q(status='R'))
            else:
                qs = qs.filter(status=status)

            if customer != 'All':
                qs = qs.filter(customer_id=customer)

            if airport != 'All':
                qs = qs.filter(airport_id=airport)


            sortField = self.request.data.get('sortField')
            # nulls last
            if sortField == 'requestDate':
                qs = qs.order_by(F('requestDate').desc(nulls_last=True))
            
            elif sortField == 'completeBy':
                qs = qs.order_by(F('completeBy').asc(nulls_last=True))

            elif sortField == 'arrivalDate':
                qs = qs.order_by(F('on_site').desc(), F('estimatedETA').asc(nulls_last=True))


            return qs


        #########################################
        # CUSTOMER

        user_profile = self.request.user.profile

        if user_profile and user_profile.customer:
            searchText = self.request.data.get('searchText')
            status = self.request.data.get('status')
            airport = self.request.data.get('airport')

            qs = Job.objects.filter(customer_id=user_profile.customer.id)

            if searchText:
                qs = qs.filter(Q(tailNumber__icontains=searchText)
                               | Q(purchase_order__icontains=searchText)
                              )

            if status == 'All':
                qs = qs.filter(Q(status='A') | Q(status='S') | Q(status='U') | Q(status='W') | Q(status='R'))
            else:
                qs = qs.filter(status=status)


            if airport != 'All':
                qs = qs.filter(airport_id=airport)


            sortField = self.request.data.get('sortField')
            if sortField == 'requestDate':
                qs = qs.order_by(F('requestDate').desc(nulls_last=True))
            
            elif sortField == 'completeBy':
                qs = qs.order_by(F('completeBy').asc(nulls_last=True))

            elif sortField == 'arrivalDate':
                qs = qs.order_by(F('on_site').desc(), F('estimatedETA').asc(nulls_last=True))


            return qs


        #########################################
        # PROJECT MANAGER

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
                  .order_by(F('completeBy').asc(nulls_last=True)) \
                  .all()


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    





