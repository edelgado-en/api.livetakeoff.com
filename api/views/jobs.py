from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from ..serializers import (
        JobSerializer,
        JobAdminSerializer,
        JobMasterPmSerializer
    )

from ..pagination import CustomPageNumberPagination
from ..models import (
        Job,
        JobServiceAssignment,
        JobRetainerServiceAssignment,
        UserCustomer,
        UserAvailableAirport
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
        
        elif self.request.user.profile.master_vendor_pm:
            return JobMasterPmSerializer

        return JobSerializer


    def get_queryset(self):
        if self.request.user.is_superuser \
          or self.request.user.is_staff \
          or self.request.user.groups.filter(name='Account Managers').exists():

            searchText = self.request.data['searchText']
            status = self.request.data['status']
            customer = self.request.data.get('customer')
            airport = self.request.data.get('airport')
            project_manager = self.request.data.get('project_manager')
            tags = self.request.data.get('tags')
            vendor = self.request.data.get('vendor')
            airport_type = self.request.data.get('airport_type', 'All')

            qs = Job.objects.prefetch_related('job_service_assignments') \
                             .prefetch_related('job_retainer_service_assignments') \
                             .prefetch_related('tags') \
                             .select_related('customer') \
                             .select_related('aircraftType')\
                             .select_related('airport') \
                             .select_related('vendor') \
                             .select_related('fbo') \
                             .all()
            
            # If project_manager then only include the jobs where the project_manager is assigned.
            # You can find the project manager in the job_service_assignments
            if project_manager != 'All':
                qs = qs.filter(Q(job_service_assignments__project_manager_id=project_manager)
                                | Q(job_retainer_service_assignments__project_manager_id=project_manager)).distinct()
                
            if tags:
                qs = qs.filter(tags__tag_id__in=tags)


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

            if vendor != 'All':
                qs = qs.filter(vendor_id=vendor)

            if airport_type != 'All':
                qs = qs.filter(airport__airport_type=airport_type)


            sortField = self.request.data.get('sortField')
            # nulls last
            if sortField == 'requestDate':
                qs = qs.order_by(F('requestDate').desc(nulls_last=True))
            
            elif sortField == 'completeBy':
                qs = qs.order_by(F('completeBy').asc(nulls_last=True))

            elif sortField == 'arrivalDate':
                qs = qs.order_by(F('on_site').desc(), F('estimatedETA').asc(nulls_last=True))


            return qs


        if self.request.user.groups.filter(name='Internal Coordinators').exists():
            searchText = self.request.data.get('searchText')
            status = self.request.data.get('status')
            customer = self.request.data.get('customer')
            airport = self.request.data.get('airport')
            project_manager = self.request.data.get('project_manager')
            tags = self.request.data.get('tags')
            airport_type = self.request.data.get('airport_type', 'All')

            qs = Job.objects.prefetch_related('job_service_assignments') \
                                .prefetch_related('job_retainer_service_assignments') \
                                .prefetch_related('tags') \
                                .select_related('customer') \
                                .select_related('aircraftType')\
                                .select_related('airport') \
                                .select_related('fbo') \
                                .all()

            user_profile = self.request.user.profile

            if not user_profile.enable_all_customers:
                user_customers = UserCustomer.objects.filter(user=self.request.user).all()
                customer_ids = []
                if user_customers:
                    for user_customer in user_customers:
                        customer_ids.append(user_customer.customer.id)
                    
                    qs = qs.filter(customer_id__in=customer_ids)

            if not user_profile.enable_all_airports:
                user_available_airports = UserAvailableAirport.objects.filter(user=self.request.user).all()

                if user_available_airports:
                    airport_ids = []
                    for user_available_airport in user_available_airports:
                        airport_ids.append(user_available_airport.airport.id)

                    qs = qs.filter(airport_id__in=airport_ids)

            # if project_manager then only include the jobs where the project_manager is assigned. You can find the project manager in the job_service_assignments
            if project_manager != 'All':
                qs = qs.filter(Q(job_service_assignments__project_manager_id=project_manager)
                                | Q(job_retainer_service_assignments__project_manager_id=project_manager)).distinct()
                
            if tags:
                qs = qs.filter(tags__tag_id__in=tags)


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

            if customer != 'All':
                qs = qs.filter(customer_id=customer)

            if airport_type != 'All':
                qs = qs.filter(airport__airport_type=airport_type)

            sortField = self.request.data.get('sortField')
            if sortField == 'requestDate':
                qs = qs.order_by(F('requestDate').desc(nulls_last=True))
            
            elif sortField == 'completeBy':
                qs = qs.order_by(F('completeBy').asc(nulls_last=True))

            elif sortField == 'arrivalDate':
                qs = qs.order_by(F('on_site').desc(), F('estimatedETA').asc(nulls_last=True))


            return qs


        if self.request.user.groups.filter(name='Project Managers').exists():
            job_ids = set()

            is_master_vendor_pm = self.request.user.profile.master_vendor_pm

            if is_master_vendor_pm:
                # Get job ids from pending services/retainer_services assigned to the current user's vendor
                # If you have at least one pending service assigned to your vendor, you can see the job
                assignments = JobServiceAssignment.objects \
                                                .select_related('job') \
                                                .filter(project_manager__profile__vendor=self.request.user.profile.vendor) \
                                                .all()

                for assignment in assignments:
                    if assignment.status != 'C':
                        job_ids.add(assignment.job.id)

            else:
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


        #########################################
        # CUSTOMER

        user_profile = self.request.user.profile

        if user_profile and user_profile.customer:
            searchText = self.request.data.get('searchText')
            status = self.request.data.get('status')
            airport = self.request.data.get('airport')
            tags = self.request.data.get('tags')
            customer = self.request.data.get('customer')

            qs = Job.objects.prefetch_related('tags').all()

            if user_profile.is_job_submitter_only:
                qs = qs.filter(created_by=self.request.user)
            
            if customer != 'All':
                qs = qs.filter(customer_id=customer)
            else:
                user_customers = UserCustomer.objects.filter(user=self.request.user).all()
                customer_ids = []
                if user_customers:
                    for user_customer in user_customers:
                        customer_ids.append(user_customer.customer.id)

                customer_ids.append(user_profile.customer.id)

                qs = qs.filter(customer_id__in=customer_ids)

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

            if tags:
                qs = qs.filter(tags__tag_id__in=tags)

            sortField = self.request.data.get('sortField')
            if sortField == 'requestDate':
                qs = qs.order_by(F('requestDate').desc(nulls_last=True))
            
            elif sortField == 'completeBy':
                qs = qs.order_by(F('completeBy').asc(nulls_last=True))

            elif sortField == 'arrivalDate':
                qs = qs.order_by(F('on_site').desc(), F('estimatedETA').asc(nulls_last=True))


            return qs



    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    





