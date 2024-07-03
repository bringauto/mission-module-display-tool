import os
import json
import time
import logging
import argparse
import threading

from flask_socketio import SocketIO
from flask import Flask, render_template, jsonify

from lib.route_manager import RouteManager
from lib.vehicles_communicator import VehiclesCommunicator

app = Flask(__name__)
socketio = SocketIO(app)

route_manager = RouteManager(socketio)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Protocol HTTP API client")
    parser.add_argument("--config", type=str, default="config/config.json", help="Path to the configuration file")
    args = parser.parse_args()
    if not os.path.exists(args.config):
        logging.error(f"Configuration file {args.config} does not exist.")
    return args


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


def start_background_thread(settings, stop_event):
    """Start the background thread for vehicle communication."""
    vehicles_communicator = VehiclesCommunicator(settings)

    def vehicle_communicator_thread():
        while not stop_event.is_set():
            try:
                time.sleep(1)
                cars = vehicles_communicator.get_all_cars_position()
                for car in cars:
                    route_manager.add_point(car)
            except Exception as e:
                logging.error(f"Exception in vehicle_communicator_thread: {e}")
                time.sleep(5)

    thread = threading.Thread(target=vehicle_communicator_thread)
    thread.daemon = True
    thread.start()
    return thread


@app.route("/")
def index():
    return render_template("index.html", route_count=len(route_manager.routes))


@app.route("/api/routes")
def get_routes():
    return jsonify({"routes": route_manager.routes})


def initialize_app(stop_event):
    """Parse args and start background thread."""
    args = parse_arguments()
    settings = load_settings(args.config)

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_background_thread(settings, stop_event)
    return settings


def run_app(port, stop_event):
    try:
        socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    try:
        stop_event = threading.Event()
        settings = initialize_app(stop_event)
        run_app(settings["port"], stop_event)

    except KeyboardInterrupt:
        logging.info("Exiting...")
        exit(0)

    except Exception as e:
        logging.error(e)
        exit(1)
