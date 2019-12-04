from django.db import models
from django.utils.translation import ugettext_lazy as _

PREVIEW_LENGTH = 20


class Comment(models.Model):

    id = models.AutoField(_("id"), primary_key=True, db_index=True)
    user_id = models.CharField(_("user id"), max_length=200)
    rating = models.DecimalField(_("rating"), null=True, blank=True, max_digits=2, decimal_places=1)
    content = models.TextField(_("comment content"), blank=True, default='')
    edited_time = models.DateTimeField(_("edited time"), auto_now_add=True)
    is_deleted = models.BooleanField(_("is valid"), null=True, blank=True, default=False)

    class Meta:
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        abstract = True

    def __str__(self):
        return f"[{self.user_id}]" + self.content[:20] + '...' if len(self.content) > 20 else self.content


class BookComment(Comment):

    book = models.ForeignKey("books.Book", db_column="book_id", on_delete=models.CASCADE, related_name='comments')

    class Meta:
        db_table = 'bookcomment'
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=0), name='rating_lowerbound'),
            models.CheckConstraint(check=models.Q(rating__lte=5), name='rating_upperbound'),
        ]
