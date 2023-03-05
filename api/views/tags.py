from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView

from api.serializers import (
    TagSerializer
)

from api.models import (
    Tag
)

class TagListView(ListAPIView):
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = Tag.objects.all()

        return qs