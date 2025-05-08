from rest_framework import serializers
from .models import Author, Category, Book, BookDetails
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name']
        validators = [
            UniqueTogetherValidator(
                queryset=Author.objects.all(),
                fields=['first_name', 'last_name'],
                message="Autor o podanym imieniu i nazwisku już istnieje."
            )
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        extra_kwargs = {
            'name': {
                'validators': [
                    UniqueValidator(
                        queryset=Category.objects.all(),
                        message="Kategoria o tej nazwie już istnieje."
                    )
                ]
            }
        }


class BookDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDetails
        fields = ['isbn', 'number_of_pages', 'language', 'publisher']


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.__str__', read_only=True)
    category_names = serializers.StringRelatedField(source='categories', many=True, read_only=True)

    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    details = BookDetailsSerializer(required=False, allow_null=True, partial=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'author',
            'author_name',
            'categories',
            'category_names',
            'description',
            'price',
            'publication_date',
            'details'
        ]

    def create(self, validated_data):
        details_data = validated_data.pop('details', None)
        book = Book.objects.create(**validated_data)
        if details_data:
            BookDetails.objects.create(book=book, **details_data)
        return book

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        instance = super().update(instance, validated_data)

        if details_data is not None:
            if hasattr(instance, 'details') and instance.details:
                details_serializer = BookDetailsSerializer(instance.details, data=details_data, partial=True)
                if details_serializer.is_valid(raise_exception=True):
                    details_serializer.save()
            elif details_data:
                BookDetails.objects.create(book=instance, **details_data)

        return instance
