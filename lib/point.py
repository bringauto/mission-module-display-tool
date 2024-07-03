from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Point:
    """
    Represents a geographical point with latitude and longitude coordinates.
    """

    lat: float
    lon: float
