def get_integer(value):
    try:
        return int(value)
    except ValueError:
        return 0
