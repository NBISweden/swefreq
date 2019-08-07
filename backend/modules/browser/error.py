class NotFoundError(Exception):
    """The query returned nothing from the database."""


class ParsingError(Exception):
    """Failed to parse the request."""


class MalformedRequest(Exception):
    """Bad request (e.g. too large region)."""
