from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
    TailIdent
)

class IdentTailLookupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, tailnumber):
        try:
            lookup = TailIdent.objects \
                                    .filter(tail_number__iexact=tailnumber).first()
            
            if lookup is None:
                return Response(None)

            return Response(lookup.ident)

        except TailIdent.DoesNotExist:
            return Response(None)