from django.db import models
from decimal import *
from django.utils.translation import ugettext_lazy as _
import django.contrib.postgres.fields as postgres
from django.core.serializers.json import DjangoJSONEncoder

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


class Resource(models.Model):

    id = models.AutoField(primary_key=True, db_index=True)
    other = postgres.JSONField(_("other information"), blank=True, encoder=DjangoJSONEncoder, default=dict)
    rating_total_score = models.PositiveIntegerField(null=True, blank=True)
    rating_number = models.PositiveIntegerField(null=True, blank=True)
    rating = models.DecimalField(_("rating"), null=True, blank=True, max_digits=2, decimal_places=1)
    img_url = models.URLField(_("image url"), blank=True, default='', max_length=500)
    # the time when the entity is edited
    edited_time = models.DateTimeField(_("edited time"), auto_now_add=True)
    is_deleted = models.BooleanField(_("is deleted"), null=False, blank=True, default=False)

    class Meta:
        verbose_name = _("resource")
        verbose_name_plural = _("resources")
        abstract = True

    def get_absolute_url(self):
        raise NotImplementedError

    def save(self):
        """ update rating before saving to db """
        # NOTE need test here
        if self.rating_number and self.rating_total_score:
            self.rating = Decimal(str(round(self.rating_total_score / self.rating_number, 1)))
        super().save()