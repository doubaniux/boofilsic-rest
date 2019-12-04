from rest_framework import serializers
from .models import Book
from comments.serializers import BookCommentSerializer


class BookSerializer(serializers.ModelSerializer):
    """
    Book serializer.
    Note that all modelfields are not included here, for example
    edited_time, since it is not supposed to be exposed to end user.
    """
    # TODO pagination of nested objects
    comments = serializers.SerializerMethodField('get_comments')

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
            'img_url',
            'rating',
            'pages',
            'edited_time'
        ]
