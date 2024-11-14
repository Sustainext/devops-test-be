from sustainapp.models import Location, Organization, Corporateentity


def get_corporate(location: Location):
    try:
        return location.corporateentity
    except AttributeError:
        return None


def get_organisation(location: Location):
    try:
        return location.corporateentity.organization
    except AttributeError:
        return None
