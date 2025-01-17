import logging
from dataclasses import asdict
from collections import defaultdict

from flask_socketio import SocketIO

from .car import Car


class RouteManager:
    """
    Class representing a route manager.

    Attributes:
        routes (defaultdict): A dictionary that stores the routes as lists of points.
        socketio: The socketio object used for emitting events.

    Methods:
        add_point: Add a point to the specified route, creating the route if it doesn't exist.
    """

    def __init__(self, socketio: SocketIO):
        self.routes: dict[str, list[dict[str, float]]] = defaultdict(list)
        self.socketio = socketio

    def add_point(self, car: Car) -> None:
        """Add a point to the specified route, creating the route if it doesn't exist."""
        route_name = car.get_name()
        point = asdict(car.last_position)
        if route_name in self.routes and len(self.routes[route_name]) > 0 and self.routes[route_name][-1] == point:
            return

        self.routes[route_name].append(point)

        logging.info(f"Added point to route {route_name}: {point}")
        self.socketio.emit("new_point", {"route_name": route_name, "point": point})
