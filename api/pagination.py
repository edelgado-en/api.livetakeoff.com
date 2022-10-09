from rest_framework import pagination
from rest_framework.response import Response

class CustomPageNumberPagination(pagination.PageNumberPagination):
    """
        Custom pagination class that extends PageNumberPagination.
        Example usage: BASE_URL/api/test-reports?page=1&size=100
    """
    page_size = 100
    page_size_query_param = 'size'
    page_query_param = 'page'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'results': data
        })