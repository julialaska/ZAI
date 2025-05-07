import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
from graphql_relay import from_global_id

from books.models import Author, Category, Book


class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name", "books")
        filter_fields = ['first_name', 'last_name']
        interfaces = (relay.Node,)


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "books")
        filter_fields = ['name']
        interfaces = (relay.Node,)


class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = (
            "id", "title", "author", "categories", "description",
            "price", "publication_date", "book_format", "cover_image"
        )
        filter_fields = {
            'title': ['exact', 'icontains', 'istartswith'],
            'price': ['exact', 'gt', 'lt', 'gte', 'lte'],
            'publication_date': ['exact', 'year', 'year__gt', 'year__lt'],
            'author__last_name': ['exact', 'icontains'],
            'categories__name': ['exact', 'icontains'],
            'book_format': ['exact'],
        }
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    all_authors = DjangoFilterConnectionField(AuthorType)
    all_categories = DjangoFilterConnectionField(CategoryType)
    all_books = DjangoFilterConnectionField(BookType)

    author = relay.Node.Field(AuthorType)
    category = relay.Node.Field(CategoryType)
    book = relay.Node.Field(BookType)


class CreateAuthor(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    author = graphene.Field(AuthorType)
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, first_name, last_name):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        if Author.objects.filter(first_name=first_name, last_name=last_name).exists():
            return cls(ok=False, errors=["Autor o tym imieniu i nazwisku już istnieje."])
        try:
            instance = Author.objects.create(first_name=first_name, last_name=last_name)
            return cls(author=instance, ok=True)
        except Exception as e:
            return cls(ok=False, errors=[f"Błąd: {e}"])


class UpdateAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        first_name = graphene.String()
        last_name = graphene.String()

    author = graphene.Field(AuthorType)
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, id, first_name=None, last_name=None):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        try:
            _, real_id = from_global_id(id)
            instance = Author.objects.get(pk=real_id)
        except Author.DoesNotExist:
            return cls(ok=False, errors=[f"Autor o ID {id} nie istnieje."])
        except Exception:
            return cls(ok=False, errors=["Nieprawidłowe ID autora."])

        updated = False
        if first_name is not None:
            instance.first_name = first_name
            updated = True
        if last_name is not None:
            instance.last_name = last_name
            updated = True

        if updated:
            if Author.objects.filter(first_name=instance.first_name, last_name=instance.last_name).exclude(
                    pk=real_id).exists():
                return cls(ok=False, errors=["Inny autor o tym imieniu i nazwisku już istnieje."])
            try:
                instance.save()
            except Exception as e:
                return cls(ok=False, errors=[f"Błąd zapisu: {e}"])
        return cls(author=instance, ok=True)


class DeleteAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    deleted_id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        try:
            _, real_id = from_global_id(id)
            instance = Author.objects.get(pk=real_id)
            instance.delete()
            return cls(ok=True, deleted_id=id)
        except Author.DoesNotExist:
            return cls(ok=False, errors=[f"Autor o ID {id} nie istnieje."])
        except Exception as e:
            return cls(ok=False, errors=[f"Błąd usuwania: {e}"])


class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()

    category = graphene.Field(CategoryType)
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, name, description=None):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        if Category.objects.filter(name=name).exists():
            return cls(ok=False, errors=["Kategoria o tej nazwie już istnieje."])
        try:
            instance = Category.objects.create(name=name, description=description or "")
            return cls(category=instance, ok=True)
        except Exception as e:
            return cls(ok=False, errors=[f"Błąd: {e}"])


class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()

    category = graphene.Field(CategoryType)
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, id, name=None, description=None):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        try:
            _, real_id = from_global_id(id)
            instance = Category.objects.get(pk=real_id)
        except Category.DoesNotExist:
            return cls(ok=False, errors=[f"Kategoria o ID {id} nie istnieje."])
        except Exception:
            return cls(ok=False, errors=["Nieprawidłowe ID kategorii."])

        updated = False
        if name is not None:
            if Category.objects.filter(name=name).exclude(pk=real_id).exists():
                return cls(ok=False, errors=["Inna kategoria o tej nazwie już istnieje."])
            instance.name = name
            updated = True
        if description is not None:
            instance.description = description
            updated = True

        if updated:
            try:
                instance.save()
            except Exception as e:
                return cls(ok=False, errors=[f"Błąd zapisu: {e}"])
        return cls(category=instance, ok=True)


class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    deleted_id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        try:
            _, real_id = from_global_id(id)
            instance = Category.objects.get(pk=real_id)
            instance.delete()
            return cls(ok=True, deleted_id=id)
        except Category.DoesNotExist:
            return cls(ok=False, errors=[f"Kategoria o ID {id} nie istnieje."])
        except Exception as e:
            return cls(ok=False, errors=[f"Błąd usuwania: {e}"])


class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author_id = graphene.ID(required=True)
        category_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
        description = graphene.String()
        price = graphene.Decimal(required=True)
        publication_date = graphene.Date(required=True)
        book_format = graphene.String()

    book = graphene.Field(BookType)
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, title, author_id, category_ids, price, publication_date, description=None,
               book_format=None):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        try:
            _, author_pk = from_global_id(author_id)
            author = Author.objects.get(pk=author_pk)
        except Author.DoesNotExist:
            return cls(ok=False, errors=[f"Autor ({author_id}) nie istnieje."])
        except:
            return cls(ok=False, errors=["Nieprawidłowe ID autora."])

        cat_pks = []
        for cat_id in category_ids:
            try:
                _, pk = from_global_id(cat_id)
                cat_pks.append(pk)
            except:
                return cls(ok=False, errors=[f"Nieprawidłowe ID kategorii: {cat_id}"])
        categories = Category.objects.filter(pk__in=cat_pks)
        if len(categories) != len(cat_pks):
            return cls(ok=False, errors=["Jedna lub więcej kategorii nie istnieje."])

        if Book.objects.filter(title=title, author=author).exists():
            return cls(ok=False, errors=["Książka tego autora o tym tytule już istnieje."])
        valid_formats = [code for code, _ in Book.FORMAT_CHOICES]
        if book_format and book_format not in valid_formats:
            return cls(ok=False, errors=[f"Nieprawidłowy format: {book_format}."])
        try:
            instance = Book.objects.create(title=title, author=author, description=description or "", price=price,
                                           publication_date=publication_date,
                                           book_format=book_format or Book._meta.get_field('book_format').get_default())
            instance.categories.set(categories)
            return cls(book=instance, ok=True)
        except Exception as e:
            return cls(ok=False, errors=[f"Błąd tworzenia książki: {e}"])


class UpdateBook(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        author_id = graphene.ID()
        category_ids = graphene.List(graphene.NonNull(graphene.ID))
        description = graphene.String()
        price = graphene.Decimal()
        publication_date = graphene.Date()
        book_format = graphene.String()

    book = graphene.Field(BookType)
    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, id, **kwargs):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        try:
            _, real_id = from_global_id(id)
            instance = Book.objects.get(pk=real_id)
        except Book.DoesNotExist:
            return cls(ok=False, errors=[f"Książka o ID {id} nie istnieje."])
        except Exception:
            return cls(ok=False, errors=["Nieprawidłowe ID książki."])

        updated_fields = False
        current_author = instance.author

        if 'title' in kwargs and kwargs['title'] is not None:
            instance.title = kwargs['title']
            updated_fields = True
        if 'description' in kwargs and kwargs['description'] is not None:
            instance.description = kwargs['description']
            updated_fields = True
        if 'price' in kwargs and kwargs['price'] is not None:
            instance.price = kwargs['price']
            updated_fields = True
        if 'publication_date' in kwargs and kwargs['publication_date'] is not None:
            instance.publication_date = kwargs['publication_date']
            updated_fields = True
        if 'book_format' in kwargs and kwargs['book_format'] is not None:
            valid_formats = [code for code, _ in Book.FORMAT_CHOICES]
            if kwargs['book_format'] not in valid_formats:
                return cls(ok=False, errors=[f"Nieprawidłowy format: {kwargs['book_format']}."])
            instance.book_format = kwargs['book_format']
            updated_fields = True

        if 'author_id' in kwargs and kwargs['author_id'] is not None:
            try:
                _, author_pk = from_global_id(kwargs['author_id'])
                current_author = Author.objects.get(pk=author_pk)
                instance.author = current_author
                updated_fields = True
            except Author.DoesNotExist:
                return cls(ok=False, errors=[f"Autor ({kwargs['author_id']}) nie istnieje."])
            except:
                return cls(ok=False, errors=["Nieprawidłowe ID autora dla aktualizacji."])

        if ('title' in kwargs and kwargs['title'] is not None) or (
                'author_id' in kwargs and kwargs['author_id'] is not None):
            if Book.objects.filter(title=instance.title, author=current_author).exclude(pk=real_id).exists():
                return cls(ok=False, errors=["Inna książka tego autora o tym tytule już istnieje."])

        if 'category_ids' in kwargs and kwargs['category_ids'] is not None:
            cat_pks = []
            for cat_id in kwargs['category_ids']:
                try:
                    _, pk = from_global_id(cat_id)
                    cat_pks.append(pk)
                except:
                    return cls(ok=False, errors=[f"Nieprawidłowe ID kategorii dla aktualizacji: {cat_id}"])
            categories = Category.objects.filter(pk__in=cat_pks)
            if len(categories) != len(cat_pks):
                return cls(ok=False, errors=[
                "Jedna lub więcej kategorii dla aktualizacji nie istnieje."])
            instance.categories.set(categories)

        if updated_fields:
            try:
                instance.save()
            except Exception as e:
                return cls(ok=False, errors=[f"Błąd zapisu książki: {e}"])

        return cls(book=instance, ok=True)


class DeleteBook(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    deleted_id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, id):
        user = info.context.user
        if not user.is_authenticated:
            return cls(ok=False, errors=["Musisz być zalogowany."])
        try:
            _, real_id = from_global_id(id)
            instance = Book.objects.get(pk=real_id)
            instance.delete()
            return cls(ok=True, deleted_id=id)
        except Book.DoesNotExist:
            return cls(ok=False, errors=[f"Książka o ID {id} nie istnieje."])
        except Exception as e:
            return cls(ok=False, errors=[f"Błąd usuwania książki: {e}"])


class Mutation(graphene.ObjectType):
    create_author = CreateAuthor.Field()
    update_author = UpdateAuthor.Field()
    delete_author = DeleteAuthor.Field()

    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

"""
PRZYKLADOWE:

mutation {
  createAuthor(firstName: "Alicja", lastName: "Nowak") {
    ok
    author {
      id
      firstName
      lastName
    }
    errors
  }
}


delete
mutation {
  deleteAuthor(id: "QXV0aG9yVHlwZToyMA==") {
    ok
    deletedId
    errors
  }
}


update
mutation {
  updateCategory(id: "Q2F0ZWdvcnlUeXBlOjE=", name: "Fantastyka Naukowa") {
    ok
    category { id name description }
    errors
  }
}

mutation {
  updateBook(
    id: "Qm9va1R5cGU6MQ==", 
    title: "Diuna (Wydanie Poprawione)",
    price: "49.90",
  ) {
    ok
    book {
      id
      title
      price
      author { firstName }
      categories { edges { node { name } } }
    }
    errors
  }
}

get
query {
  allAuthors {
    edges {
      node {
        id
        firstName
        lastName
        books {
          edges {
            node {
              id
              title
            }
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}

get book of author
query {
  author(id: "QXV0aG9yVHlwZTo4") {
    id
    firstName
    lastName
    books {
      edges {
        node {
          title
        }
      }
    }
  }
}
"""
