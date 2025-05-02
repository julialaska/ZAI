from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Author, Book, Category
import datetime


def get_user_credentials():
    return {'username': 'tester', 'password': 'password123'}


class AuthorAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(first_name="Adam", last_name="Mickiewicz")
        cls.author2 = Author.objects.create(first_name="Olga", last_name="Tokarczuk")
        cls.user = User.objects.create_user(**get_user_credentials())

    def test_list_authors(self):
        url = reverse('author-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 2)
        else:
            self.assertEqual(len(response.data), 2)

    def test_retrieve_author(self):
        url = reverse('author-detail', kwargs={'pk': self.author1.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], self.author1.first_name)

    def test_create_author_unauthenticated(self):
        url = reverse('author-list')
        data = {'first_name': 'Nowy', 'last_name': 'Pisarz'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_author_authenticated(self):
        url = reverse('author-list')
        self.client.force_authenticate(user=self.user)
        data = {'first_name': 'Henryk', 'last_name': 'Sienkiewicz'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Author.objects.count(), 3)
        self.assertEqual(Author.objects.latest('id').first_name, 'Henryk')
        self.client.force_authenticate(user=None)

    def test_create_author_duplicate(self):
        url = reverse('author-list')
        self.client.force_authenticate(user=self.user)
        data = {'first_name': self.author1.first_name, 'last_name': self.author1.last_name}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('już istnieje', response.data['non_field_errors'][0])
        self.assertEqual(Author.objects.count(), 2)
        self.client.force_authenticate(user=None)

    def test_update_author_authenticated(self):
        url = reverse('author-detail', kwargs={'pk': self.author2.pk})
        self.client.force_authenticate(user=self.user)
        updated_data = {'first_name': 'Olga', 'last_name': 'Tokarczuk-Nowak'}
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author2.refresh_from_db()
        self.assertEqual(self.author2.last_name, 'Tokarczuk-Nowak')
        self.client.force_authenticate(user=None)

    def test_delete_author_authenticated(self):
        url = reverse('author-detail', kwargs={'pk': self.author1.pk})
        initial_count = Author.objects.count()
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Author.objects.count(), initial_count - 1)
        self.client.force_authenticate(user=None)


class CategoryAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category1 = Category.objects.create(name="Powieść historyczna", description="Opis powieści historycznej")
        cls.category2 = Category.objects.create(name="Fantasy", description="Opis fantasy")
        cls.user = User.objects.create_user(**get_user_credentials())

    def test_list_categories(self):
        url = reverse('category-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 2)
        else:
            self.assertEqual(len(response.data), 2)

    def test_retrieve_category(self):
        url = reverse('category-detail', kwargs={'pk': self.category1.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.category1.name)

    def test_create_category_unauthenticated(self):
        url = reverse('category-list')
        data = {'name': 'Science Fiction'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_authenticated(self):
        url = reverse('category-list')
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Literatura piękna', 'description': 'Klasyka literatury'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Category.objects.latest('id').name, 'Literatura piękna')
        self.client.force_authenticate(user=None)

    def test_create_category_duplicate(self):
        url = reverse('category-list')
        self.client.force_authenticate(user=self.user)
        data = {'name': self.category1.name}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('już istnieje', response.data['name'][0])
        self.assertEqual(Category.objects.count(), 2)
        self.client.force_authenticate(user=None)

    def test_update_category_authenticated(self):
        url = reverse('category-detail', kwargs={'pk': self.category2.pk})
        self.client.force_authenticate(user=self.user)
        updated_data = {'description': 'Nowy opis dla Fantasy'}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category2.refresh_from_db()
        self.assertEqual(self.category2.description, 'Nowy opis dla Fantasy')
        self.assertEqual(self.category2.name, 'Fantasy')
        self.client.force_authenticate(user=None)

    def test_delete_category_authenticated(self):
        url = reverse('category-detail', kwargs={'pk': self.category1.pk})
        initial_count = Category.objects.count()
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), initial_count - 1)
        self.client.force_authenticate(user=None)


class BookAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(first_name="Adam", last_name="Mickiewicz")
        cls.author2 = Author.objects.create(first_name="Olga", last_name="Tokarczuk")
        cls.category1 = Category.objects.create(name="Epos")
        cls.category2 = Category.objects.create(name="Powieść")

        cls.book1 = Book.objects.create(
            title="Pan Tadeusz", author=cls.author1, description="Epos narodowy.",
            price=Decimal('29.99'), publication_date=datetime.date(1834, 6, 28)
        )
        cls.book1.categories.add(cls.category1)

        cls.book2 = Book.objects.create(
            title="Księgi Jakubowe", author=cls.author2, description="Monumentalna powieść.",
            price=Decimal('59.90'), publication_date=datetime.date(2014, 10, 1)
        )
        cls.book2.categories.add(cls.category2)

        cls.book3 = Book.objects.create(
            title="Dziady cz. III", author=cls.author1, description="Dramat romantyczny.",
            price=Decimal('19.50'), publication_date=datetime.date(1832, 1, 1)
        )
        cls.book3.categories.add(cls.category1)

        cls.user = User.objects.create_user(**get_user_credentials())

    def test_list_books_unauthenticated(self):
        url = reverse('book-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(len(response.data['results']), 3)
            self.assertEqual(response.data['results'][0]['title'], self.book3.title)
        else:
            self.assertEqual(len(response.data), 3)

    def test_create_book_unauthenticated(self):
        url = reverse('book-list')
        data = {'title': 'Nowa Książka', 'author': self.author1.id, 'price': Decimal('9.99'),
                'publication_date': '2023-01-01'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_book_authenticated(self):
        url = reverse('book-list')
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Lalka',
            'author': self.author2.id,
            'categories': [self.category2.id],
            'price': "35.00",
            'publication_date': '1890-01-01',
            'description': 'Powieść Bolesława Prusa.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 4)
        new_book = Book.objects.latest('id')
        self.assertEqual(new_book.title, 'Lalka')
        self.assertEqual(new_book.categories.count(), 1)
        self.client.force_authenticate(user=None)

    def test_create_book_duplicate(self):
        url = reverse('book-list')
        self.client.force_authenticate(user=self.user)
        data = {
            'title': self.book1.title,
            'author': self.book1.author.id,
            'categories': [self.category1.id],
            'price': '50.00',
            'publication_date': '2023-10-10'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertIn('unique set', response.data['non_field_errors'][0])
        self.assertEqual(Book.objects.count(), 3)
        self.client.force_authenticate(user=None)

    def test_retrieve_book(self):
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertIsInstance(response.data['category_names'], list)
        self.assertIn(self.category1.name, response.data['category_names'])

    def test_update_book_authenticated(self):
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        self.client.force_authenticate(user=self.user)
        updated_data = {
            'title': 'Pan Tadeusz (Wydanie II)',
            'author': self.author1.id,
            'price': "32.50",
            'publication_date': self.book1.publication_date.isoformat(),
            'categories': [self.category1.id, self.category2.id],
            'description': self.book1.description,
            'book_format': self.book1.book_format,
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Pan Tadeusz (Wydanie II)')
        self.assertEqual(self.book1.price, Decimal('32.50'))
        self.assertEqual(self.book1.categories.count(), 2)
        self.client.force_authenticate(user=None)

    def test_partial_update_book_authenticated(self):
        url = reverse('book-detail', kwargs={'pk': self.book2.pk})
        self.client.force_authenticate(user=self.user)
        updated_data = {'price': "65.00"}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book2.refresh_from_db()
        self.assertEqual(self.book2.price, Decimal('65.00'))
        self.assertEqual(self.book2.title, "Księgi Jakubowe")
        self.client.force_authenticate(user=None)

    def test_delete_book_authenticated(self):
        url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        initial_count = Book.objects.count()
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), initial_count - 1)
        self.client.force_authenticate(user=None)

    def test_create_book_missing_title(self):
        url = reverse('book-list')
        self.client.force_authenticate(user=self.user)
        data = {
            'author': self.author1.id,
            'categories': [self.category1.id],
            'price': "15.00",
            'publication_date': '2023-11-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('required', response.data['title'][0])
        self.client.force_authenticate(user=None)

    def test_create_book_invalid_price(self):
        url = reverse('book-list')
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Książka z błędem ceny',
            'author': self.author1.id,
            'categories': [self.category1.id],
            'price': "liczba",
            'publication_date': '2023-11-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
        self.assertIn('valid number', response.data['price'][0])
        self.client.force_authenticate(user=None)

    def test_create_book_non_existent_author(self):
        url = reverse('book-list')
        self.client.force_authenticate(user=self.user)
        non_existent_author_id = 9999
        data = {
            'title': 'Książka Widmo',
            'author': non_existent_author_id,
            'categories': [self.category1.id],
            'price': "20.00",
            'publication_date': '2023-11-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('author', response.data)
        self.assertIn('Invalid pk', response.data['author'][0])
        self.client.force_authenticate(user=None)

    def test_book_filtering_by_price(self):
        url = reverse('book-list')
        response = self.client.get(url + '?price__lt=30', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 2)
        titles = {book['title'] for book in results}
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book3.title, titles)
        self.assertNotIn(self.book2.title, titles)

    def test_book_filtering_by_author(self):
        url = reverse('book-list')
        response = self.client.get(url + f'?author={self.author1.id}', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 2)
        titles = {book['title'] for book in results}
        self.assertIn(self.book1.title, titles)
        self.assertIn(self.book3.title, titles)

    def test_book_searching(self):
        url = reverse('book-list')
        response = self.client.get(url + '?search=Tadeusz', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], self.book1.title)

        response = self.client.get(url + '?search=powieść', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], self.book2.title)

    def test_book_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url + '?ordering=price', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        prices = [Decimal(book['price']) for book in results]
        self.assertEqual(prices, [Decimal('19.50'), Decimal('29.99'), Decimal('59.90')])

        response = self.client.get(url + '?ordering=-publication_date', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        dates = [book['publication_date'] for book in results]
        self.assertEqual(dates, ['2014-10-01', '1834-06-28', '1832-01-01'])

    def test_statistics_endpoint(self):
        url = reverse('book-statistics')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('aggregate_stats', response.data)
        self.assertIn('average_price', response.data['aggregate_stats'])
        self.assertIn('total_books', response.data['aggregate_stats'])
        self.assertEqual(response.data['aggregate_stats']['total_books'], 3)
        self.assertIn('books_per_author', response.data)
        self.assertTrue(len(response.data['books_per_author']) > 0)