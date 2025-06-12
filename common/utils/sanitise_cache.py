def sanitize_cache_key_part(s):
    if s is None:
        return "none"
    # Convert to string and replace unsafe characters
    return (
        str(s)
        .replace(" ", "_")
        .replace("/", "_")
        .replace(":", "_")
        .replace("(", "_")
        .replace(")", "_")
    )
