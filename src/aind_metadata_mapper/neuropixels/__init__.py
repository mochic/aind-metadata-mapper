"""Maps neuropixels related metadata."""

class NeuropixelsRigException(Exception):
    """General error for MVR."""


UNSUPPORTED_VERSION_WARNING_TEMPLATE = \
    "Detected version: %s not in supported versions: %s"
