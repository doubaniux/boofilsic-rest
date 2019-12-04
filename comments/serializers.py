from rest_framework import serializers
from core.validators import ValidUniqueTogetherValidator
from core.serializers import PrimayKeyHyperlinkField
from .models import BookComment
from books.models import Book


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
