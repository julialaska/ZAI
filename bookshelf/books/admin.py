from django.contrib import admin
from .models import Author, Category, Book, BookDetails


class BookDetailsInline(admin.StackedInline):
    model = BookDetails
    can_delete = False
    verbose_name_plural = 'Szczegóły książki'


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

    inlines = [BookDetailsInline]

    def display_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = 'Categories'

    def has_details(self, obj):
        try:
            return bool(obj.details and obj.details.pk is not None)
        except BookDetails.DoesNotExist:
            return False
    has_details.boolean = True
