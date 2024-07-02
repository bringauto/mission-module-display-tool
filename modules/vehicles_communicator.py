import requests
import time
import logging
from modules.point import Point
from modules.car import Car


class VehiclesCommunicator:
    """
    A class that communicates with the vehicles API to retrieve vehicle information and positions.
    """
    class AuthenticationException(Exception):
        pass

    class ApiUnavailableException(Exception):
        pass

    def __init__(self, settings):
        self._url = settings["api-url"]
        self._params = {"api_key": settings["api-key"], "wait": True, "since": 0}
        logging.info(f"Initializing with API URL: {self._url}")
        self._wait_till_api_is_available()

    def _wait_till_api_is_available(self):
        logging.info("Waiting for Protocol HTTP API to become available.")
        while True:
            try:
                response = requests.get(f"{self._url}/cars", params=self._params)
                logging.info(f"Got API response from fleet protocol: {response.status_code}")
                if response.status_code == 200:
                    break
                elif response.status_code == 401:
                    raise self.AuthenticationException("Invalid API key.")

                else:
                    logging.error(f"Unexpected error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                logging.warning("Protocol HTTP API is not available. Retrying in 5 seconds.")

            time.sleep(5)
        logging.info("Protocol HTTP API is available.")

    def _access_nested_dict(self, dict_obj, keys):
        for key in keys:
            if key in dict_obj:
                dict_obj = dict_obj[key]
            else:
                return None
        return dict_obj

    def _get_telemetry(self, device):
        return self._access_nested_dict(device, ["payload", "data", "telemetry", "position"])

    def _send_request(self, url_postfix):
        try:
            response = requests.get(f"{self._url}{url_postfix}", params=self._params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error: {e.response.status_code}")
            if e.response.status_code == 401:
                raise ValueError("Invalid API key.") from e

            else:
                self._wait_till_api_is_available()
                return self._send_request(url_postfix)

        except requests.exceptions.ConnectionError:
            logging.error("Failed to connect to Protocol HTTP API. Retrying.")
            self._wait_till_api_is_available()
            return self._send_request(url_postfix)

    def get_position(self, car):
        request_url = f"/status/{car['company_name']}/{car['car_name']}"
        car_status_json = self._send_request(request_url)

        if car_status_json:
            device = car_status_json[-1]
            position = self._get_telemetry(device)
            if position:
                return Point(position.get("latitude"), position.get("longitude"))
        return None

    def get_all_cars_position(self):
        cars_json = self._send_request("/cars")
        cars = []

        if cars_json:
            for car in cars_json:
                point = self.get_position(car)
                if point:
                    cars.append(Car(car["company_name"], car["car_name"], point))
        return cars
