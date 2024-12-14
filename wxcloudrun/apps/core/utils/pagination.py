from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    """标准分页类"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'results': data
        })
        
class SmallResultsSetPagination(StandardResultsSetPagination):
    """小分页类"""
    page_size = 5
    
class LargeResultsSetPagination(StandardResultsSetPagination):
    """大分页类"""
    page_size = 50 