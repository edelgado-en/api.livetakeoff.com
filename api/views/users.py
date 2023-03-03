from django.db.models import Q
from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from ..pagination import CustomPageNumberPagination

from api.serializers import UsersSerializer


class UsersView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination
    serializer_class = UsersSerializer

    def get_queryset(self):
        name = self.request.data.get('name')
        # role can be project manager group, admin group, account manager group, or customer. A customer is determined by the customer field in the user profile.
        # if the role is 'All', then do not filter by role
        role = self.request.data.get('role')

        users = User.objects.filter(is_active=True) \
                            .select_related('profile') \
                            .order_by('first_name', 'last_name')
        
        open_jobs_only = self.request.data.get('open_jobs_only', False)
        
        if name:
            users = users.filter(Q(first_name__icontains=name)
                                    | Q(last_name__icontains=name)
                                    | Q(username__icontains=name))

        if open_jobs_only:
            users = users.filter(Q(job_service_assignments__status__in=['A', 'W']) 
                                | Q(job_retainer_service_assignments__status__in=['A', 'W'])).distinct()
            
            users = users.filter(Q(job_service_assignments__job__status__in=['A', 'S', 'U', 'W'])
                                  | Q(job_retainer_service_assignments__job__status__in=['A', 'S', 'U', 'W'])).distinct()


        if role != 'All':
            if role == 'Customers':
                users = users.filter(profile__customer__isnull=False)
            
            elif role == 'Project Managers' or role == 'Account Managers':
                users = users.filter(groups__name=role)
            
            elif role == 'Admins':
                users = users.filter(is_staff=True)
            
            elif role == 'Internal Coordinators':
                users = users.filter(groups__name=role)


        return users


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)