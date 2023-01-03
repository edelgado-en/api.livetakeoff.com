from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

from api.serializers import (TailAlertSerializer)
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from api.models import (TailAlert)


class TailAlertsView(ListAPIView):
    serializer_class = TailAlertSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination


    def get_queryset(self):
        searchText = self.request.data.get('searchText','')

        queryset = TailAlert.objects.filter(Q(message__icontains=searchText)
                                             | Q(tailNumber__icontains=searchText)) \
                                    .order_by('-created_at')

        return queryset


    def post(self, request, *args, **kwargs):
        if not self.can_view_alerts(request.user):
            return Response({'error': 'You do not have permission to view tail alerts'}, status=status.HTTP_403_FORBIDDEN)

        return self.list(request, *args, **kwargs)


    def delete(self, request, *args, **kwargs):
        if not self.can_view_alerts(request.user):
            return Response({'error': 'You do not have permission to view tail alerts'}, status=status.HTTP_403_FORBIDDEN)

        tail_alert = get_object_or_404(TailAlert, pk=kwargs.get('id'))
        tail_alert.delete()

        return Response({'success': 'Tail alert has been deleted'}, status=status.HTTP_200_OK)


    def patch(self, request, *args, **kwargs):
        if not self.can_view_alerts(request.user):
            return Response({'error': 'You do not have permission to view tail alerts'}, status=status.HTTP_403_FORBIDDEN)

        tail_alert = get_object_or_404(TailAlert, pk=kwargs.get('id'))
        tail_alert.message = request.data.get('message')
        tail_alert.updated_at = datetime.now()

        tail_alert.save()

        serializer = TailAlertSerializer(tail_alert)

        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def can_view_alerts(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        return False