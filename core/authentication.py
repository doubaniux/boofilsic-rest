from hashlib import sha256
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework import exceptions
from boofilsic.settings import SECRET_KEY


class SimpleAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        # get request header Secret-Key
        key = request.META.get('HTTP_SECRET_KEY').lower()

        # auth not attempted
        if not key:
            msg = _("Authentication required. Please attach SHA256 encrypted secret key in http header 'Secret-Key'.")
            raise exceptions.AuthenticationFailed(msg)

        # auth attempted
        if key == self.__hash(SECRET_KEY):
            return (None, True)
        else:
            msg = _('Authentication failed.')
            raise exceptions.AuthenticationFailed(msg)

    def __hash(self, raw_str):
        """
        hash secret key using sha256
        """
        raw = raw_str.encode()
        return sha256(raw).hexdigest()
