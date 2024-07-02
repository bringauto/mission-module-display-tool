from dataclasses import dataclass


@dataclass(slots=True)
class Point:
    """
    Represents a geographical point with latitude and longitude coordinates.
    """

    lat: float
    lon: float

    def get_as_dict(self):
        """
        Returns the point as a dictionary with 'lat' and 'lon' keys.
        """
        return {"lat": self.lat, "lon": self.lon}
