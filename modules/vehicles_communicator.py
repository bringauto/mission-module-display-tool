import requests
import time
import logging


class VehiclesCommunicator:
    def __init__(self, settings):
        self.url = settings["api-url"]
        self.params = {"api_key": settings["api-key"], "wait": True, "since": settings["since"]}
        logging.info(f"Initializing with API URL: {self.url}")
        self.__wait_till_api_is_available()
        self.__init_vehicles_positions()

    def __wait_till_api_is_available(self):
        while True:
            try:
                response = requests.get(f"{self.url}/cars", params=self.params)
                logging.info(f"Protocol response: {response.status_code}")
                if response.status_code == 200:
                    break
                elif response.status_code == 401:
                    raise ValueError("Invalid API key.")

                elif response.status_code == 404:
                    logging.error("Protocol HTTP API is not available.")
                    exit(1)
                else:
                    logging.error(f"Unexpected error: {response.status_code}")
                    time.sleep(5)
            except requests.exceptions.ConnectionError:
                logging.warning("Protocol HTTP API is not available. Retrying in 5 seconds.")
                time.sleep(5)

    def __init_vehicles_positions(self):
        self.vehicles_positions = {}
        cars_json = self.__send_request("/cars")
        if cars_json:
            for car in cars_json:
                self.vehicles_positions[f"{car['company_name']}/{car['car_name']}"] = []

    def __access_nested_dict(self, dict_obj, keys):
        for key in keys:
            if key in dict_obj:
                dict_obj = dict_obj[key]
            else:
                return None
        return dict_obj
    
    def __get_telemetry(self, device):
        return self.__access_nested_dict(device, ["payload", "data", "telemetry", "position"])

    def __send_request(self, url_postfix):
        try:
            response = requests.get(f"{self.url}{url_postfix}", params=self.params)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error: {e.response.status_code}")
            if e.response.status_code == 401:
                raise ValueError("Invalid API key.")

            elif e.response.status_code == 404:
                raise ValueError("Protocol HTTP API is not available.")

            else:
                self.__wait_till_api_is_available()
                return self.__send_request(url_postfix)

        except requests.exceptions.ConnectionError:
            logging.error("Failed to connect to Protocol HTTP API. Retrying.")
            self.__wait_till_api_is_available()
            return self.__send_request(url_postfix)

    def get_position(self, car):
        request_url = f"/status/{car['company_name']}/{car['car_name']}"
        car_status_json = self.__send_request(request_url)
        
        if car_status_json:
            device = car_status_json[-1]
            position = self.__get_telemetry(device)
            if position:
                return {"lat": position.get("latitude"), "lon": position.get("longitude")}
        return None

    def get_all_cars_position(self):
        cars_json = self.__send_request("/cars")
        cars_positions = {}
        logging.debug(f"Received cars: {cars_json}")

        if cars_json:
            for car in cars_json:
                position = self.get_position(car)
                if position:
                    car_key = f"{car['company_name']}/{car['car_name']}"
                    cars_positions[car_key] = position
        return cars_positions
