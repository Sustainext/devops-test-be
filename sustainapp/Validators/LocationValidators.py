from rest_framework.exceptions import ValidationError


def validate_latitude(value):
    print(type(value), value)
    if value > 90.000000 or value < -90.0:
        raise ValidationError(f"{value} exceeds 90 degree range")
    else:
        print("not raising error in validate_latitude")
    whole, decimal = str(value).split(".")
    length_whole = len(whole)
    length_decimal = len(decimal)

    print("whole,decimal", whole, decimal)

    if length_whole > 5 and length_decimal > 6:
        raise ValidationError(f"{value} exceeds 9 digits.")
    if length_whole == 5:
        raise ValidationError(f"{value} does not include correct + or - sign.")
    if length_whole == 5:
        raise ValidationError(f"{value} does not include correct + or - sign.")


def validate_longitude(value):
    print(type(value), value)
    if value > 180.0 or value < -180.0:
        raise ValidationError(f"{value} exceeds 180 degree range")
    else:
        print("not raising error in validate_longitude")
    whole, decimal = str(value).split(".")
    length_whole = len(whole)
    length_decimal = len(decimal)

    print("whole,decimal", whole, decimal)

    if length_whole > 5 and length_decimal > 6:
        raise ValidationError(f"{value} exceeds 9 digits.")
    if length_whole == 5 and length_whole[0] != "-":
        raise ValidationError(f"{value} does not include correct + or - sign.")
    if length_whole == 5 and length_whole[0] != "-":
        raise ValidationError(f"{value} does not include correct + or - sign.")
