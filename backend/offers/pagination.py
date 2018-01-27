from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class InfiniteScrollPagination(PageNumberPagination):
    page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'has_more': self.page.has_next(),
            'total_count': self.page.paginator.count,
            'results': data
        })
