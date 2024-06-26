import logging


class RouteManager:
    def __init__(self, socketio):
        self.routes = []
        self.socketio = socketio

    def add_point(self, route_name, point):
        """Add a point to the specified route, creating the route if it doesn't exist."""
        for route in self.routes:
            if route["name"] == route_name:
                if len(route["points"]) > 0 and route["points"][-1] == point:
                    return
                route["points"].append(point)
                break
        else:
            new_route = {"name": route_name, "points": [point]}
            self.routes.append(new_route)

        logging.info(f"Added point to route {route_name}: {point}")
        self.socketio.emit("new_point", {"route_name": route_name, "point": point})
