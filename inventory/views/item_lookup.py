from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from inventory.models import (
    Item
)

class ItemLookupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, name):
        # only return 200 to avoid showing a 404 to the user
        try:
            # ignore case
            item = Item.objects.filter(name__iexact=name).first()

            if item:
                return Response({'id': item.id}, status=status.HTTP_200_OK)
            else:
                return Response({'id': 0}, status=status.HTTP_200_OK)
        
        except Item.DoesNotExist:
            return Response({'id': 0}, status=status.HTTP_200_OK)