import logging
from collections import defaultdict
from flask_socketio import SocketIO
from modules.car import Car


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
        self.routes: dict[str, list[Car]] = defaultdict(list)
        self.socketio = socketio

    def add_point(self, car: Car):
        """Add a point to the specified route, creating the route if it doesn't exist."""
        route_name = car.get_name()
        point = car.last_position.get_as_dict()
        if route_name in self.routes:
            if len(self.routes[route_name]) > 0 and self.routes[route_name][-1] == point:
                return

        self.routes[route_name].append(point)

        logging.info(f"Added point to route {route_name}: {point}")
        self.socketio.emit("new_point", {"route_name": route_name, "point": point})
