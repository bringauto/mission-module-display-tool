from dataclasses import dataclass

from .point import Point


@dataclass(slots=True, frozen=True)
class Car:
    """
    Represents a car object.

    Attributes:
        company_name (str): The name of the car company.
        car_name (str): The name of the car.
        last_position (Point): The last position of the car.
    """

    company_name: str
    car_name: str
    last_position: Point

    def get_name(self) -> str:
        """
        Returns the name of the car in the format 'company_name/car_name'.

        Returns:
            str: The name of the car.
        """
        return f"{self.company_name}/{self.car_name}"
