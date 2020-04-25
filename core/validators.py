from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import qs_filter


class ValidUniqueTogetherValidator(UniqueTogetherValidator):
    """
    Unique together validation that excludes objects with `is_deleted=False`.

    """

    def filter_queryset(self, attrs, queryset, serializer):
        """
        Filter the queryset to all instances matching the given attributes.
        """
        # field names => field sources
        sources = [
            serializer.fields[field_name].source
            for field_name in self.fields
        ]

        # If this is an update, then any unprovided field should
        # have it's value set based on the existing instance attribute.
        if serializer.instance is not None:
            for source in sources:
                if source not in attrs:
                    attrs[source] = getattr(serializer.instance, source)

        # Determine the filter keyword arguments and filter the queryset.
        filter_kwargs = {
            source: attrs[source]
            for source in sources
        }
        # NOTE this is the only modification from original class method
        filter_kwargs['is_deleted'] = False
        return qs_filter(queryset, **filter_kwargs)
