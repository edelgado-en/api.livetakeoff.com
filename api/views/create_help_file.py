from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from api.models import (Help)

from api.serializers import (HelpFileSerializer)

class CreateHelpFileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = HelpFileSerializer

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        description = request.data.get('description')
        file = request.data.get('file')
        url = request.data.get('video_url')
        photo = request.data.get('photo')
        access_level = request.data.get('access_level', 'A')
        file_type = request.data.get('file_type')

        p = Help(name=name,
                   description=description,
                    file=file,
                    photo=photo,
                    url=url,
                    file_type=file_type,
                    access_level=access_level,
                    uploaded_by=request.user)
        
        p.save()

        serializer = HelpFileSerializer(p)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    def delete(self, request, id):
        helpFile = Help.objects.get(pk=id)
        helpFile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, id):
        helpFile = Help.objects.get(pk=id)
        helpFile.name = request.data.get('name')
        helpFile.description = request.data.get('description')
        helpFile.access_level = request.data.get('access_level', 'A')
        helpFile.save()
        
        serializer = HelpFileSerializer(helpFile)
       
        return Response(serializer.data, status=status.HTTP_200_OK)