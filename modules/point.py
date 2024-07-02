from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    lat: float
    lon: float

    def get_as_dict(self):
        return {"lat": self.lat, "lon": self.lon}
