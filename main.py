from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import time
from modules.vehicles_communicator import VehiclesCommunicator
import os
import webbrowser

app = Flask(__name__)
socketio = SocketIO(app)

routes = []

def add_point_to_route(route_name, point):
    global routes

    for route in routes:
        if route["name"] == route_name:
            if len(route['points']) > 0 and route['points'][-1] == point:
                return
            route['points'].append(point)
            break
    else:
        new_route = {"name": route_name, "points": [point]}
        routes.append(new_route)

    print(f"Added point to route {route_name}: {point}")
    socketio.emit('new_point', {'route_name': route_name, 'point': point})

def vc_thread():
    vc = VehiclesCommunicator()
    webbrowser.open_new('http://localhost:5000/')
    while True:
        time.sleep(1)
        positions = vc.get_positions()
        for route_name, points in positions.items():
            if points:
                add_point_to_route(route_name, points[0])

def start_background_thread():
    thread = threading.Thread(target=vc_thread)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    return render_template('index.html', route_count=len(routes))

@app.route('/api/routes')
def get_routes():
    return jsonify({'routes': routes})

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        start_background_thread()

    socketio.run(app, debug=True)
