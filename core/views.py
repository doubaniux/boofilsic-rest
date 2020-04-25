"""
Extended generic view classes from django rest framework.
`is_deleted` and `edited_time` are required fields for any model that involves these view classes.
"""

from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import FieldDoesNotExist
from django.http import Http404
from django.utils import timezone


class ListCreateView(generics.ListCreateAPIView):
    """
    Filter out instances with field is_deleted=False while retrieving instance list.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        check_is_deleted_field(queryset.model)
        queryset = queryset.filter(is_deleted=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        check_is_deleted_field(serializer.Meta.model)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Filter out instances with field `is_deleted=False` while retrieving.
    `Delete` will set is_deleted=Flase instead of directly removing the record from database.
    If deleting from database is desired, add parameter `hard=true` in the request json body.

    UPDATE and PATCH will always update edited_time.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        check_is_deleted_field(instance._meta.model)
        # transfer all data keys into lowercase
        cleaned_params = dict((k.lower(), v) for k, v in request.query_params.items())
        if cleaned_params.get('hard') == 'false':
            if instance.is_deleted:
                raise Http404
            self.perform_destroy(instance)
            msg = {'hard': False}
            code = status.HTTP_200_OK
        else:
            self.perform_hard_destroy(instance)
            msg = None
            code = status.HTTP_204_NO_CONTENT     
        return Response(data=msg, status=code)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

    def perform_hard_destroy(self, instance):
        instance.delete()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        check_is_deleted_field(instance._meta.model)
        if instance is not None and not instance.is_deleted:
            serializer = self.get_serializer(instance)
        else:
            raise Http404
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        check_edited_time_field(instance._meta.model)
        instance.edited_time = timezone.now()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


def check_is_deleted_field(model):
    """
    Check if the model has field `is_deleted`
    """
    if not hasattr(model, 'is_deleted'):
        raise FieldDoesNotExist("Can't find `is_deleted` field for model `%s`." % model)


def check_edited_time_field(model):
    """
    Check if the model has field `is_deleted`
    """
    if not hasattr(model, 'edited_time'):
        raise FieldDoesNotExist("Can't find `edited_time` field for model `%s`." % model)
