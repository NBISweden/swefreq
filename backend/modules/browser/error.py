class NotFoundError(Exception):
    """The query returned nothing from the database."""
    pass

class ParsingError(Exception):
    """Failed to parse the request."""
    pass

class MalformedRequest(Exception):
    """Bad request (e.g. too large region)."""
    pass
