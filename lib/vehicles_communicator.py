import time
import logging

from .car import Car as UiCar
from .point import Point as UiPoint

from urllib3.exceptions import MaxRetryError
from fleet_http_client_python import ApiClient, Configuration, CarApi, DeviceApi, Car # type: ignore
from fleet_http_client_python.exceptions import UnauthorizedException # type: ignore

class VehiclesCommunicator:
    """
    A class that communicates with the vehicles API to retrieve vehicle information and positions.
    """

    class AuthenticationException(Exception):
        pass


    def __init__(self, settings):
        api_configuration = Configuration(
            host=str(settings["api-url"]),
            api_key={'AdminAuth': str(settings["api-key"])}
        )
        api_configuration.retries = 0
        api_client = ApiClient(api_configuration)
        self._car_api = CarApi(api_client)
        self._device_api = DeviceApi(api_client)
        logging.info(f"Initializing with API URL: {str(settings['api-url'])}")
        self._wait_till_api_is_available()
        self._last_car_timestamps = {}


    def _wait_till_api_is_available(self):
        logging.info("Waiting for Protocol HTTP API to become available.")
        while True:
            try:
                self._car_api.available_cars(wait=True, since=0)
                logging.info("Got response from fleet protocol API.")
                break
            except UnauthorizedException:
                raise self.AuthenticationException("Invalid API key.")
            except MaxRetryError:
                logging.warning("Protocol HTTP API is not available. Retrying in 5 seconds.")
            except Exception as e:
                logging.warning(f"Unexpected error: {e}. Retrying in 5 seconds.")

            time.sleep(5)
        logging.info("Protocol HTTP API is available.")


    def _get_position(self, data):
        try:
            return data.get("telemetry").get("position")
        except:
            return None


    def _construct_car_name(self, car: Car) -> str:
        return car.company_name + "/" + car.car_name


    def _send_request(self, function):
        try:
            return function()
        except UnauthorizedException:
            raise self.AuthenticationException("Invalid API key.")
        except MaxRetryError:
            logging.error("Failed to connect to Protocol HTTP API. Retrying.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}. Retrying.")

        self._wait_till_api_is_available()
        return self._send_request(function)


    def get_point(self, car: Car) -> UiPoint | None:
        car_identification = self._construct_car_name(car)
        car_statuses = self._send_request(
            lambda: self._device_api.list_statuses(car.company_name,
                                                   car.car_name,
                                                   since=self._last_car_timestamps[car_identification],
                                                   wait=False)
        )

        if car_statuses:
            self._last_car_timestamps[car_identification] = car_statuses[-1].timestamp
            payload = car_statuses[-1].payload.data.to_dict()
            position = self._get_position(payload)
            if position:
                return UiPoint(position.get("latitude"), position.get("longitude"))
        return None


    def get_all_cars_position(self) -> list[UiCar]:
        cars = self._send_request(
            lambda: self._car_api.available_cars(wait=True, since=0)
        )
        for car in cars:
            car_identification = self._construct_car_name(car)
            if car_identification not in self._last_car_timestamps:
                self._last_car_timestamps[car_identification] = 0

        ret: list[UiCar] = []
        if cars:
            for car in cars:
                point = self.get_point(car)
                if point:
                    ret.append(UiCar(car.company_name, car.car_name, point))
        return ret
