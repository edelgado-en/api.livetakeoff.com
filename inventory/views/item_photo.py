from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.contrib.auth.models import User

from inventory.models import Item

class ItemPhotoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request):
        photo = request.data['photo']
        item_id = request.data['itemId']

        item = Item.objects.get(id=item_id)

        item.photo = photo

        item.save()

        content = {
            'photo': item.photo.url
        }

        return Response(content, status.HTTP_200_OK);