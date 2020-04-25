from rest_framework import serializers
from .models import Book, BookComment
from core.validators import ValidUniqueTogetherValidator
from core.serializers import PrimayKeyHyperlinkField
from drf_base64.fields import Base64ImageField


class BookSerializer(serializers.ModelSerializer):
    """
    Book serializer.
    Note that all modelfields are not included here, for example
    edited_time, since it is not supposed to be exposed to end user.
    """
    # TODO pagination of nested objects
    comments = serializers.SerializerMethodField('get_comments')
    cover = Base64ImageField(required=False)

    def get_comments(self, book):
        """
        Use commentserializer to exclude objects with is_delete=true.
        """
        comments_set = book.comments.filter(is_deleted=False)
        serializer = BookCommentSerializer(
            comments_set,
            many=True,
            context={'request': self.context['request']}
        )
        return serializer.data

    class Meta:
        model = Book
        fields = [
            'id',
            'title',
            'subtitle',
            'orig_title',
            'translator',
            'author',
            'pub_house',
            'pub_year',
            'pub_month',
            'binding',
            'isbn',
            'price',
            'comments',
            'language',
            'other',
            'rating',
            'rating_number',
            'pages',
            'cover',
            'edited_time'
        ]


class BookCommentSerializer(serializers.ModelSerializer):
    """
    Book comment.
    """
    book = PrimayKeyHyperlinkField(
        queryset=Book.objects.filter(is_deleted=False),
        view_name="books:book_retrieve_update_delete",
        lookup_url_kwarg="book_id",
    )

    class Meta:
        model = BookComment
        fields = [
            'id',
            'user_id',
            'rating',
            'content',
            'book',
            'edited_time'
        ]
        validators = [
            ValidUniqueTogetherValidator(
                queryset=BookComment.objects.all(),
                fields=['user_id', 'book']
            )
        ]