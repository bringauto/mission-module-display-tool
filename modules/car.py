from dataclasses import dataclass
from modules.point import Point

@dataclass(slots=True)
class Car:
    company_name: str
    car_name: str
    last_position: Point = Point(0, 0)

    def get_name(self):
        return f"{self.company_name}/{self.car_name}"
    