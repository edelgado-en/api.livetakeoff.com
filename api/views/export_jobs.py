from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from django_q.models import OrmQ, Task  # ORM broker queue + results

from django.contrib.auth.models import User

from ..serializers import (ExportJobSerializer)
from rest_framework.generics import ListAPIView
from api.models import ExportJob

from ..pagination import CustomPageNumberPagination

class ExportJobsView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ExportJobSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        status = self.request.data.get('status', 'All')
        customer = self.request.data.get('customer', 'All')
        searchText = self.request.data.get('searchText')

        qs = ExportJob.objects.all()

        if searchText:
            qs = qs.filter(Q(filename__icontains=searchText))

        if status != 'All':
            qs = qs.filter(status=status)


        # if the current user is a customer, only show export jobs created by the current user
        if self.request.user.profile.customer:
            qs = qs.filter(user=self.request.user)
        else:
            if customer != 'All':
                qs = qs.filter(customer_id=customer)

        qs = qs.order_by('-created_at')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        try:
            ej = ExportJob.objects.get(pk=kwargs['id'])
        except ExportJob.DoesNotExist:
            raise Http404

        # If it’s queued but not started → remove from queue and delete the row
        if ej.status == ExportJob.Status.PENDING:
            if ej.task_id:
                # Remove from the ORM broker if not yet picked up
                OrmQ.objects.filter(key=ej.task_id).delete()
            
            ej.status = ExportJob.Status.CANCELED
            ej.save(update_fields=["status"])
            ej.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)

        # If it’s running → request cooperative cancel; do NOT delete yet
        if ej.status == ExportJob.Status.RUNNING:
            if not ej.cancel_requested:
                ej.cancel_requested = True
                ej.save(update_fields=["cancel_requested"])
            
            # Option A: return 409 and tell UI “Cancel requested; job will stop shortly”
            return Response(
                {"detail": "Cancel requested. Job will stop shortly; you can delete it after it stops."},
                status=status.HTTP_200_OK,
            )

        # If it already finished/canceled/failed → safe to delete
        if ej.task_id:
            Task.objects.filter(id=ej.task_id).delete()
        
        ej.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)