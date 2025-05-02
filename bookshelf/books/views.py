from rest_framework import viewsets, permissions, generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Avg, Count, Min, Max

from .models import Author, Category, Book
from .serializers import AuthorSerializer, CategorySerializer, BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by('last_name', 'first_name')
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'author': ['exact'],
        'categories': ['exact'],
        'publication_date': ['year', 'month', 'day', 'gte', 'lte'],
        'price': ['exact', 'gt', 'lt', 'gte', 'lte'],
    }

    search_fields = ['title', 'description']

    ordering_fields = ['title', 'price', 'publication_date', 'author__last_name']
    ordering = ['title']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = Book.objects.aggregate(
            average_price=Avg('price'),
            total_books=Count('id'),
            min_price=Min('price'),
            max_price=Max('price')
        )
        books_per_author = Author.objects.annotate(num_books=Count('books')).values('first_name', 'last_name', 'num_books')

        return Response({
            "aggregate_stats": stats,
            "books_per_author": list(books_per_author)
        })
