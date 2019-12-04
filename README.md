# Boofilsic
A RESTful web API service, serves books, films and records.

## Dependency
- Python 3.6+
- Django 2.2.x
- Django REST Framework 3.10.x

## Configuration
### Database
Edit `setting.py`. By default using PostgreSQL.
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'donotban',
        'USER': 'donotban',
        'PASSWORD': 'pleasedonotban',
        'HOST': 'x.x.x.x',
        'OPTIONS': {
            'client_encoding': 'UTF8',
            # 'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_DEFAULT,
        }
    }
}
```

### Migration
Make initial migrations
```bash
$ python manage.py makemigrations
```
If working with existing resource tables, apply migrations with parameter `--fake`, for example
```bash
$ python manage.py migrate books --fake
```

### Deployment
Check the [Django official doc](https://docs.djangoproject.com/en/2.2/howto/deployment/).
Beware that http server software might exclude unrecognized custom header, which will cause authentication fail.

## REST API
All resources are returned in **JSON** format.

### Authentication
This project adopts a simple application level authentication. Every request should contains a custom header `Secret-Key`, whose value should be the hashed SECRET_KEY using `SHA256` in `setting.py`.

### Book
#### GET /books/
Return a list of books according to query parameters.
**In current version, search result will be returned disorderly.**

| querystring param | description | required |
|-------------------|-------------|----------|
| `page` | Pagination index. Default is 1. |❌|
| `page_size` | How many books should be returned on one page. Default is 100, max is 1000.|❌|
| `title` | Fuzzy search. Searching fields are `title` and `sub_title`. Support multiple keywords separated by `space`. |❌|
| `author` | Search according to author. Searching field is `author`. |❌|
| `translator` | Search according to translator. Searching field is `translator`. |❌|
| `pub_house` | Search according to publishing house.|❌|
| `after` | Lower bound of published date filtering. Filtering fields are `pub_year` and `pub_month`. Format should be `%Y-%m` or `%Y`. |❌|
| `before` | Upper bound of published date filtering. Format is the same as `after`. |❌|
| `isbn` | Hard search. Searching field is `isbn`. Will discard `title` is specified.|❌|
| `higher_than` | Lower bound of rating filtering. Filtering field is `rating`.|❌|
| `lower_than` | Upper bound of rating filtering. Filtering field is `rating`.|❌|

#### GET /books/:id/
Return an individual book.

#### GET /books/:id/comments/
Return a list of comments related to the book.

| querystring param | description | required |
|-------------------|-------------|----------|
| `page` | Pagination index. Default is 1. |❌|
| `page_size` | How many books should be returned on one page. Default is 100, max is 1000.|❌|

#### GET /books/:book_id/comments/:comment_id/
Return the comment specified by `comment_id`.

#### POST /books/
Add a new book.

| json param | description | required |
|------------|-------------|----------|
| `title` | String |✔|
| `isbn` | String or Integer. Must be unique. |✔|
| `subtitle` | String |❌|
| `orig_title` | Original title. String|❌|
| `author` | String array |❌|
| `translator` | String array|❌|
| `pub_house` |Publishing house. String|❌|
| `pub_year` | Integer |❌|
| `pub_month` | Integer |❌|
| `binding` | String |❌|
| `price` | String. But Integer is suggested. |❌|
| `comments` ||❌|
| `language` | String. 2-Letter language code. Note that not all codes in [ISO 639-1](https://www.wikiwand.com/en/ISO_639-1) are allowed.|❌|
| `other` | Any other information about the book. This is a nested json field.|❌|
| `img_url` | URL string. Book cover image.|❌|
| `pages` | Integer |❌|

#### POST /books/:id/comments/
Add a new book comment.

| json param | description | required |
|------------|-------------|----------|
| `user_id` | String |✔|
| `rating` | Numeric. Must be one in sequence `0, 0.5, 1.0, ..., 5.0` |❌|
| `content` | String. Text content of the comment. |❌|

#### PUT /books/:id/
Update a book. Parameters are the same as the POST method.
Note that only required fields will be validated, unrequired fields will not be updated if not speicified explicitly.

#### PUT /books/:book_id/comments/:comment_id/
Update a book comment. Parameters are the same as the POST method.
Note that only required fields will be validated, unrequired fields will not be updated if not speicified explicitly.

#### DELETE /books/:id/
Delete a book. By default the record will not be removed from the database, if that is desired, use query string.

| querystring param | description | required |
|-------------------|-------------|----------|
| `hard` | When this is `true`, remove a record completely from the database. |❌|

**Request without `hard=true` will not result in cascade deletion.**

#### DELETE /books/:book_id/comments/:comment_id/
Delete a book comment. By default the record will not be removed from the database, if that is desired, use query string.

| querystring param | description | required |
|-------------------|-------------|----------|
| `hard` | When this is `true`, remove a record completely from the database. |❌|

#### PATCH /books/:id/
Partially update a book. Parameters are the same as the POST method.

#### PATCH /books/:book_id/comments/:comment_id/
Partially update a book comment. Parameters are the same as the POST method.

## TODO
- Films service
- Records service
- Pre-make initial migration file and add RunSQL to it
 