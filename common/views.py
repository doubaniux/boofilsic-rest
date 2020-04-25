from django.db import IntegrityError
from django.db import transaction
from django.utils import timezone
from core import views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


# common comment classes
class CommentListCreateView(views.ListCreateView):
    """
    Comment list create view, validates rating.
    """

    # for example book/file/record
    resource_name = None
    resource_url_kwarg = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.resource_name is not None, "`resource_name` required."
        if self.resource_url_kwarg is None:
            self.resource_url_kwarg = self.resource_name + '_id'

    def create(self, request, *args, **kwargs):
        """
        Get resource id from url params, before passing the request to serializers,
        so that users don't have to specify resource id explicitly.
        """

        # when no resource_id specified, get pk from url;
        # explicity resource pk is supported but not recommended.
        if not request.data.get(self.resource_name):
            # self.kwargs holds all url params
            pk = self.kwargs.get(self.resource_url_kwarg)
        else:
            try:
                pk = int(request.data.get(self.resource_name))
            except ValueError:
                raise ValidationError({'detail': f"`{self.resource_name}` must be an integer."})
        request.data[self.resource_name] = pk

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Handle rating constraints
        """
        try:
            with transaction.atomic():
                resource = serializer.validated_data.get(self.resource_name)
                rating = serializer.validated_data.get('rating', None)
                self.update_resource_rating(resource, rating)
                try:
                    serializer.save()
                except IntegrityError as e:
                    if "rating" in e.__str__():
                        msg = {'detail': "Rating out of range. Ensure it is between [0, 5]."}
                        raise ValidationError(msg)
                    else:
                        raise e
        except IntegrityError as e:
            raise IntegrityError(
                "Integrity error occurred when creating new comment. " + e.__str__()
            )

    def update_resource_rating(self, resource, rating):
        validate_rating(rating)
        assert hasattr(resource, 'comments'), (
            "`%s` has no field `comments`."
            % resource.__class__.__name__
        )
        if rating is None:
            return
        if resource.rating is not None:
            resource.rating_number += 1
            resource.rating_total_score += int(rating * 2)
        else:
            resource.rating_number = 1
            resource.rating_total_score = int(rating * 2)
        resource.save()


class CommentRetrieveUpdateDestroyView(views.RetrieveUpdateDestroyView):
    """
    Handle rating.
    DELETE PATCH UPDATE will change rating.
    """

    # for example book/file/record
    resource_name = None
    resource_url_kwarg = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.resource_name is not None, "`resource_name` required."
        if self.resource_url_kwarg is None:
            self.resource_url_kwarg = self.resource_name + '_id'

    def perform_destroy(self, instance):
        resource = getattr(instance, self.resource_name)
        assert hasattr(resource, 'comments'), (
            "`%s` has no field `comments`."
            % resource.__class__.__name__
        )
        try:
            with transaction.atomic():
                if instance.rating:
                    self.decrease_resource_rating(resource, instance.rating)
                instance.is_deleted = True
                instance.save()
        except IntegrityError as e:
            raise IntegrityError(
                "Integrity error occurred when deleting comment. " + e.__str__()
            )

    def perform_hard_destroy(self, instance):
        resource = getattr(instance, self.resource_name)
        assert hasattr(resource, 'comments'), (
            "`%s` has no field `comments`."
            % resource.__class__.__name__
        )
        try:
            with transaction.atomic():
                if instance.rating:
                    self.decrease_resource_rating(resource, instance.rating)
                instance.delete()
        except IntegrityError as e:
            raise IntegrityError(
                "Integrity error occurred when deleting comment in hard mode. " + e.__str__()
            )

    def update(self, request, *args, **kwargs):
        # NOTE it is not a good practice to overwrite udpate() here
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        views.check_edited_time_field(instance._meta.model)
        instance.edited_time = timezone.now()

        # for PUT method, get resource id from url
        if not partial and request.data.get(self.resource_name, None) is None:
            request.data[self.resource_name] = self.kwargs.get(self.resource_url_kwarg)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer, instance):
        try:
            with transaction.atomic():
                resource = getattr(instance, self.resource_name)
                new_rating = serializer.validated_data.get('rating', None)
                old_rating = instance.rating
                self.update_resource_rating(resource, old_rating, new_rating, serializer.partial)
                try:
                    serializer.save()
                except IntegrityError as e:
                    if "rating" in e.__str__():
                        msg = {'detail': "Rating out of range. Ensure it is between [0, 5]."}
                        raise ValidationError(msg)
                    else:
                        raise e
        except IntegrityError as e:
            raise IntegrityError(
                "Integrity error occurred when updating comment. " + e.__str__()
            )

    def decrease_resource_rating(self, resource, old_rating):
        """ adjust the rating of resource when deleting comment """
        assert hasattr(resource, 'comments'), (
            "`%s` has no field `comments`."
            % resource.__class__.__name__
        )
        if resource.rating_number == 1:
            resource.rating = None
            resource.rating_number = None
            resource.rating_total_score = None
        elif resource.rating_number >= 2:
            resource.rating_number -= 1;
            resource.rating_total_score -= int(old_rating * 2)
        resource.save()

    def update_resource_rating(self, resource, old_rating, new_rating, partial):
        """ update the resource rating when update or partially update """
        validate_rating(new_rating)
        assert hasattr(resource, 'comments'), (
            "`%s` has no field `comments`."
            % resource.__class__.__name__
        )

        if old_rating == new_rating:
            return
        if new_rating is not None:
            # # exclude "deleted" objects to keep integrity
            # rating_quantity = resource.comments.filter(is_deleted=False).exclude(rating=None).count()
            # # XOR conditions to test integrity of db
            # if (resource.rating is not None and rating_quantity == 0)\
            # or (resource.rating is None and rating_quantity != 0):
            #     raise IntegrityError("comment rating and resource rating don't match.")
            if resource.rating is None:
                resource.rating_total_score = int(new_rating * 2)
                resource.rating_number = 1
            else:
                # add new rating to resource
                if old_rating is None:
                    resource.rating_number += 1
                    resource.rating_total_score += int(new_rating * 2)
                # update rating
                else:
                    resource.rating_total_score += int((new_rating - old_rating) * 2)
            resource.save()
        else:
            # old_rating is not None and new_rating is None, substract rating from resource.

            # specified null rating and non-specified rating will both be cleaned
            # to be None by serializer's validation. Access request data to distinguish.
            # Assume rating is not mandatory, PUT and PATCH will have the same effect
            # on rating field.
            if 'rating' in self.request.data and self.request.data.get('rating') is None:
                self.decrease_resource_rating(resource, old_rating)


def validate_rating(rating):
    """
    Check if input rating is in str sequence 0.0, 0.5, ..., 5.0.
    """
    if rating is None:
        return True
    valid_choices = [str(x / 10) for x in range(0, 55, 5)]
    if str(rating) in valid_choices:
        return True
    else:
        msg = {'detail': "Rating must be one of %s" % str([float(x) for x in valid_choices])}
        raise ValidationError(msg) 