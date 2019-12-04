from django.db import models
from django.utils.translation import ugettext_lazy as _
import django.contrib.postgres.fields as postgres
from django.core.serializers.json import DjangoJSONEncoder


class Book(models.Model):
    """
    Book entity class.
    Created according to https://book.douban.com.
    Only title and isbn are required, the other fields are optional.
    """

    # considering that rewirting the fields collection operation of django
    # is re-inventing the wheel and sweating, maybe hard-code is a better choice XD
    LANGUAGE_CHOICE = [
        ('af', 'af'), ('ar', 'ar'), ('be', 'be'), ('bg', 'bg'), ('ca', 'ca'), ('cs', 'cs'), 
        ('da', 'da'), ('de', 'de'), ('el', 'el'), ('en', 'en'), ('es', 'es'), ('et', 'et'), 
        ('eu', 'eu'), ('fa', 'fa'), ('fi', 'fi'), ('fo', 'fo'), ('fr', 'fr'), ('ga', 'ga'), 
        ('gd', 'gd'), ('he', 'he'), ('hi', 'hi'), ('hr', 'hr'), ('hu', 'hu'), ('id', 'id'), 
        ('is', 'is'), ('it', 'it'), ('ja', 'ja'), ('ji', 'ji'), ('ko', 'ko'), ('ko', 'ko'), 
        ('lt', 'lt'), ('lv', 'lv'), ('mk', 'mk'), ('ms', 'ms'), ('mt', 'mt'), ('nl', 'nl'), 
        ('no', 'no'), ('pl', 'pl'), ('pt', 'pt'), ('rm', 'rm'), ('ro', 'ro'), ('ru', 'ru'), 
        ('sb', 'sb'), ('sk', 'sk'), ('sl', 'sl'), ('sq', 'sq'), ('sr', 'sr'), ('sv', 'sv'), 
        ('sx', 'sx'), ('sz', 'sz'), ('th', 'th'), ('tn', 'tn'), ('tr', 'tr'), ('ts', 'ts'), 
        ('uk', 'uk'), ('ur', 'ur'), ('ve', 've'), ('vi', 'vi'), ('xh', 'xh'), ('zh', 'zh'), 
        ('zu', 'zu'), ('unknown', 'unknown')
    ]

    # todo:
    # figure out that if every field needs null or blank to be ture or false
    # read more about meta
    id = models.AutoField(primary_key=True, db_index=True)
    # widely recognized name, usually in Chinese
    title = models.CharField(_("title"), max_length=200)
    subtitle = models.CharField(_("subtitle"), blank=True, default='', max_length=200)
    # original name, for books in foreign language
    orig_title = models.CharField(_("original title"), blank=True, default='', max_length=200)

    author = postgres.ArrayField(
        models.CharField(_("author"), blank=True, default='', max_length=100),
        null=True,
        blank=True,
        default=list,
    )
    translator = postgres.ArrayField(
        models.CharField(_("translator"), blank=True, default='', max_length=100),
        null=True,
        blank=True,
        default=list,
    )
    language = models.CharField(_("language"), blank=True, default='unknown', max_length=10, choices=LANGUAGE_CHOICE)
    pub_house = models.CharField(_("publishing house"), blank=True, default='', max_length=200)
    pub_year = models.IntegerField(_("published year"), null=True, blank=True)
    pub_month = models.IntegerField(_("published month"), null=True, blank=True)
    binding = models.CharField(_("binding"), blank=True, default='', max_length=50)
    # since data origin is not formatted and might be CNY USD or other currency, use char instead
    price = models.CharField(_("pricing"), blank=True, default='', max_length=20)
    pages = models.PositiveIntegerField(_("pages"), null=True, blank=True)
    isbn = models.CharField(_("ISBN"), blank=True, max_length=20, unique=True, db_index=True)
    # any other non-standard info, eg: imprint/series/......
    other = postgres.JSONField(_("other information"), blank=True, encoder=DjangoJSONEncoder, default=dict)
    img_url = models.URLField(_("image url"), blank=True, default='', max_length=500)
    rating = models.DecimalField(_("rating"), null=True, blank=True, max_digits=64, decimal_places=63)
    # the time when the entity is edited
    edited_time = models.DateTimeField(_("edited time"), auto_now_add=True)
    is_deleted = models.BooleanField(_("is deleted"), null=False, blank=True, default=False)

    class Meta:
        # more info: https://docs.djangoproject.com/en/2.2/ref/models/options/
        verbose_name = _("Book")
        verbose_name_plural = _("Books")
        # set managed=False if the model represents an existing table or
        # a database view that has been created by some other means.
        # check the link above for further info
        managed = True
        db_table = 'book'
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=0), name='rating_lowerbound'),
            models.CheckConstraint(check=models.Q(rating__lte=5), name='rating_upperbound'),
            models.CheckConstraint(check=models.Q(rating__gte=0), name='pub_year_lowerbound'),
            models.CheckConstraint(check=models.Q(rating__lte=12), name='pub_month_upperbound'),
            models.CheckConstraint(check=models.Q(rating__gte=1), name='pub_month_lowerbound'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        raise NotImplementedError
        # return reverse("Book_detail", kwargs={"pk": self.pk})