from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import qs_filter


class ValidUniqueTogetherValidator(UniqueTogetherValidator):
    """
    Unique together validation that excludes objects with `is_deleted=False`.

    TODO return hyperlink if constraint check failed
    """

    def filter_queryset(self, attrs, queryset):
        """
        Filter the queryset to all instances matching the given attributes.
        """
        # If this is an update, then any unprovided field should
        # have it's value set based on the existing instance attribute.
        if self.instance is not None:
            for field_name in self.fields:
                if field_name not in attrs:
                    attrs[field_name] = getattr(self.instance, field_name)

        # Determine the filter keyword arguments and filter the queryset.
        filter_kwargs = {
            field_name: attrs[field_name]
            for field_name in self.fields
        }

        # NOTE this is the only modification from original class method
        filter_kwargs['is_deleted'] = False

        return qs_filter(queryset, **filter_kwargs)
