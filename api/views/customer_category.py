from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
        Customer,
        CustomerCategory,
        JobCategory
    )

class CustomerCategoryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        customer = get_object_or_404(Customer, pk=id)
        name = request.data.get('name')
        category_id = request.data.get('category_id')
        action = request.data.get('action', 'add')

        if action == 'add' and name == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'add':
            # ignore case sensitivity
            if CustomerCategory.objects.filter(name__iexact=name, customer=customer).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            p = CustomerCategory(customer=customer, name=name)

            p.save()

            return Response(status=status.HTTP_201_CREATED)

        if action == 'delete':
            #Ensure there are no JobCategories associated with this CustomerCategory
            if JobCategory.objects.filter(customer_category_id=category_id).exists():
                return Response({'error': 'Cannot delete category with associated job categories'}, status=status.HTTP_400_BAD_REQUEST)
            
            p = CustomerCategory.objects.get(id=category_id, customer=customer)

            p.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        
        if action == 'make_active':
            p = CustomerCategory.objects.get(id=category_id, customer=customer)

            p.is_active = True
            p.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        
        if action == 'remove_active':
            p = CustomerCategory.objects.get(id=category_id, customer=customer)

            p.is_active = False
            p.save()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
