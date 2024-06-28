from sustainapp.models import Location, Corporateentity, Organization
from django.db.models import Prefetch
from rest_framework import serializers


def set_locations_data(organisation, corporate, location):
    """
    If Organisation is given and Corporate and Location is not given, then get all corporate locations
    If Corporate is given and Organisation and Location is not given, then get all locations of the given corporate
    If Location is given, then get only that location
    """
    if organisation and corporate and location:
        locations = Location.objects.filter(id=location.id)
    elif location is None and corporate and organisation:
        locations = corporate.location.all()
    elif location is None and corporate is None and organisation:
        locations = Location.objects.prefetch_related(
            Prefetch(
                "corporateentity",
                queryset=organisation.corporatenetityorg.all(),
            )
        ).filter(corporateentity__in=organisation.corporatenetityorg.all())
    else:
        raise serializers.ValidationError(
            "Not send any of the following fields: organisation, corporate, location"
        )

    return locations
