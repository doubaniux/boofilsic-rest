from django.urls import path
from .views import BookListCreate
from .views import BookRetrieveUpdateDestroy
from comments.views import BookCommentListCreate
from comments.views import BookCommentRetrieveUpdateDestroy


app_name = 'books'
urlpatterns = [
    path('', BookListCreate.as_view(), name="book_list_create"),
    path('<int:book_id>/', BookRetrieveUpdateDestroy.as_view(), name="book_retrieve_update_delete"),
    path('<int:book_id>/comments/', BookCommentListCreate.as_view(), name="book_comment_list_create"),
    path('<int:book_id>/comments/<int:comment_id>/', BookCommentRetrieveUpdateDestroy.as_view(), name="book_retrieve_update_delete"),
]
