from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from api.models import Job
from ..serializers import (
        JobCompletedSerializer,
        JobAdminSerializer
    )


class CompletedJobsListView(ListAPIView):
    serializer_class = JobCompletedSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        searchText = self.request.data['searchText']
        status = self.request.data['status']

        requestedDateFrom = self.request.data.get('requestedDateFrom')
        requestedDateTo = self.request.data.get('requestedDateTo')

        arrivalDateFrom = self.request.data.get('arrivalDateFrom')
        arrivalDateTo = self.request.data.get('arrivalDateTo')

        departureDateFrom = self.request.data.get('departureDateFrom')
        departureDateTo = self.request.data.get('departureDateTo')

        completeByDateFrom = self.request.data.get('completeByDateFrom')
        completeByDateTo = self.request.data.get('completeByDateTo')

        qs = Job.objects.select_related('airport') \
                        .select_related('customer') \
                        .select_related('fbo') \
                        .select_related('aircraftType') \
                        .order_by('status') \
                        .all()    

        if searchText:
                qs = qs.filter(Q(tailNumber__icontains=searchText)
                               | Q(customer__name__icontains=searchText)
                               | Q(purchase_order__icontains=searchText)
                               | Q(airport__initials__icontains=searchText)
                              )

        if status == 'All':
            qs = qs.filter(Q(status='C') | Q(status='I') | Q(status='T'))
        else:
            qs = qs.filter(status=status)

        # apply date range filters
        if arrivalDateFrom:
            qs = qs.filter(estimatedETA__gte=arrivalDateFrom)

        if arrivalDateTo:
            qs = qs.filter(estimatedETA__lte=arrivalDateTo)

        if requestedDateFrom:
            qs = qs.filter(requestDate__gte=requestedDateFrom)

        if requestedDateTo:
            qs = qs.filter(requestDate__lte=requestedDateTo)

        if departureDateFrom:
            qs = qs.filter(estimatedETD__gte=departureDateFrom)

        if departureDateTo:
            qs = qs.filter(estimatedETD__lte=departureDateTo)

        if completeByDateFrom:
            qs = qs.filter(completeBy__gte=completeByDateFrom)

        if completeByDateTo:
            qs = qs.filter(completeBy__lte=completeByDateTo)

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