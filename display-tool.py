import os
import json
import time
import logging
import argparse
import threading
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from modules.vehicles_communicator import VehiclesCommunicator
from modules.route_manager import RouteManager

app = Flask(__name__)
socketio = SocketIO(app)

route_manager = RouteManager(socketio)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Protocol HTTP API client")
    parser.add_argument("--config", type=str, default="resources/config.json", help="Path to the configuration file")
    arguments = parser.parse_args()
    validate_config_path(arguments.config)
    return arguments


def validate_config_path(config_path):
    """Check if the configuration file exists."""
    if not os.path.exists(config_path):
        logging.error(f"Configuration file {config_path} does not exist.")
        exit(1)


def load_settings(config_path):
    """Load settings from the configuration file."""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load configuration file {config_path}: {e}")
        exit(1)


def start_background_thread(settings, stop_event):
    """Start the background thread for vehicle communication."""

    def vc_thread():
        vehicles_communicator = VehiclesCommunicator(settings)
        while not stop_event.is_set():
            time.sleep(1)
            positions = vehicles_communicator.get_all_cars_position()
            logging.info(f"Received positions: {positions}")
            for route_name, point in positions.items():
                if point:
                    route_manager.add_point(route_name, point)

    thread = threading.Thread(target=vc_thread)
    thread.daemon = True
    thread.start()
    return thread


@app.route("/")
def index():
    return render_template("index.html", route_count=len(route_manager.routes))


@app.route("/api/routes")
def get_routes():
    return jsonify({"routes": route_manager.routes})


def initialize_app():
    """Initialize the Flask app and start the server."""
    args = parse_arguments()
    settings = load_settings(args.config)

    stop_event = threading.Event()
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_background_thread(settings, stop_event)

    return stop_event


def run_app(stop_event):
    try:
        socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S"
    )
    try:
        stop_event = initialize_app()
        run_app(stop_event)

    except Exception as e:
        logging.error(e)
        exit(1)
