from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import CustomerTail
from api.serializers.customer_tail import CustomerTailSerializer

class CustomerTailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        customer_tail = get_object_or_404(CustomerTail, pk=id)
        serializer = CustomerTailSerializer(customer_tail, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)