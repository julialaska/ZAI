from django.contrib import admin
from .models import Author, Category, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name')
    search_fields = ('last_name', 'first_name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'publication_date', 'display_categories')
    list_filter = ('publication_date', 'author', 'categories', 'price')
    search_fields = ('title', 'description', 'author__first_name', 'author__last_name')
    date_hierarchy = 'publication_date'
    filter_horizontal = ('categories',)

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Categories'
