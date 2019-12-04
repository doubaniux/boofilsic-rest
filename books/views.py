import re
from core import views
from .models import Book
from .serializers import BookSerializer
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ParseError


class BookListCreate(views.ListCreateView):
    serializer_class = BookSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle isbn unique constraint.
        """
        assert 'isbn' in request.data, "isbn not in create book post."
        try:
            former_book = Book.objects.get(isbn=request.data['isbn'])
            if former_book.is_deleted:
                msg = f"Book with the same isbn `{former_book.isbn}` already" + \
                "exists in the database, but it is marked as deleted. You must" + \
                "delete the old one with `hard=ture` first."
                raise ParseError({'detail': msg})
        except ObjectDoesNotExist:
            pass
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        """
        filter objects according to query string.
        pagination is handled at `self.list()`
        """
        def title(value, query_args):
            q = Q()
            keywords = value.split()
            for keyword in keywords:
                q = q | Q(title__icontains=keyword)
                q = q | Q(subtitle__istartswith=keyword)
                q = q | Q(orig_title__icontains=keyword)
            query_args.append(q)

        def author(value, query_args):
            query_args.append(Q(author__icontains=value))

        def translator(value, query_args):
            query_args.append(Q(translator__icontains=value))

        def pub_house(value, query_args):
            query_args.append(Q(pub_house__icontains=value))

        def after(value, query_args):
            """ publishing date lower bound """
            numbers = re.findall(r'\d+', value)
            if len(numbers) > 2:
                raise ParseError({'detail': "Wrong format."})
            elif len(numbers) == 2:
                # year less than month
                if numbers[0] < numbers[1]:
                    raise ParseError({'detail': "Wrong format."})
                query_args.append(
                    Q(pub_year__gte=numbers[0]) &\
                    ~( Q(pub_year=numbers[0]) & Q(pub_month__lte=numbers[1]) )
                )
            elif len(numbers) == 1:
                query_args.append(Q(pub_year__gte=numbers[0]))

        def before(value, query_args):
            """ publishing date upper bound """
            numbers = re.findall(r'\d+', value)
            if len(numbers) > 2:
                raise ParseError({'detail': "Wrong format."})
            elif len(numbers) == 2:
                # year less than month
                if numbers[0] < numbers[1]:
                    raise ParseError({'detail': "Wrong format."})
                query_args.append(
                    Q(pub_year__lte=numbers[0]) &\
                    ~( Q(pub_year=numbers[0]) & Q(pub_month__gte=numbers[1]) )
                )
            elif len(numbers) == 1:
                query_args.append(Q(pub_year__lte=numbers[0]))

        def isbn(value, query_args):
            query_args.append(Q(isbn=value))

        def higher_than(value, query_args):
            """ rating lower bound """
            query_args.append(Q(rating__gte=value))
            # book rating not  right?

        def lower_than(value, query_args):
            """ rating upper bound """
            query_args.append(Q(rating__lte=value))

        handler = {
            'title': title,
            'author': author,
            'translator': translator,
            'pub_house': pub_house,
            'after': after,
            'before': before,
            'isbn': isbn,
            'higher_than': higher_than,
            'lower_than': lower_than,
        }

        query_params = dict((k.lower(), v) for k, v in self.request.query_params.items())
        query_args = []
        for k, v in query_params.items():
            if k in handler:
                handler[k](v, query_args)

        queryset = Book.objects.filter(*query_args)
        return queryset


class BookRetrieveUpdateDestroy(views.RetrieveUpdateDestroyView):
    """
    It is strongly recommended delete book object with `hard=true`
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_url_kwarg = 'book_id'

