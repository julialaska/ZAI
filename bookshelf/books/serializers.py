from rest_framework import serializers
from .models import Author, Category, Book
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


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.__str__', read_only=True)
    category_names = serializers.StringRelatedField(source='categories', many=True, read_only=True)

    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)

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
            'publication_date'
        ]
