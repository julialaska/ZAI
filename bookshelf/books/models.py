from django.db import models
from django.utils import timezone


class PublishedBookManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(publication_date__lte=timezone.now().date())

    def affordable(self):
        return self.get_queryset().filter(price__lt=20.00)


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Writer"
        verbose_name_plural = "Writers"
        constraints = [
            models.UniqueConstraint(fields=['first_name', 'last_name'], name='unique_author_full_name')
        ]


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"


class Book(models.Model):
    FORMAT_CHOICES = [
        ('HB', 'Hardback'),
        ('PB', 'Paperback'),
        ('EB', 'Ebook'),
    ]

    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    categories = models.ManyToManyField(Category, related_name='books')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    publication_date = models.DateField()
    book_format = models.CharField(max_length=2, choices=FORMAT_CHOICES, default='PB')

    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    objects = models.Manager()
    published = PublishedBookManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publication_date', 'title']
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'], name='unique_author_title')
        ]


class BookDetails(models.Model):
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='details'
    )
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="ISBN")
    number_of_pages = models.PositiveIntegerField(blank=True, null=True, verbose_name="Liczba stron")
    language = models.CharField(max_length=50, blank=True, verbose_name="Język")
    publisher = models.CharField(max_length=100, blank=True, verbose_name="Wydawca")

    def __str__(self):
        return f"Szczegóły dla: {self.book.title}"

    class Meta:
        verbose_name_plural = "Szczegóły książek"
