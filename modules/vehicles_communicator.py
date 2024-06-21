import requests
import time

class VehiclesCommunicator:
    def __init__(self):
        self.url = 'http://localhost:8080/v2/protocol'
        self.params = {
            'api_key': 'ProtocolStaticAccessKey',
            'wait': 'true',
            'since': '0'
        }
        self.__is_http_api_available()
        self.__init_vehicles_positions()

    def __is_http_api_available(self):
        while True:
            try:
                response = requests.get(self.url + "/cars", params=self.params)
                if response.status_code != 404:
                    break
            except requests.exceptions.ConnectionError:
                print("HTTP API is not available. Retrying in 5 seconds.")
                time.sleep(5)

    def __init_vehicles_positions(self):
        self.vehicles_positions = {}
        cars_json = self.__send_request("/cars")
        print(cars_json)

        for car in cars_json:
            self.vehicles_positions[car["company_name"] + "/" + car["car_name"]] = []

    def __send_request(self, url_postfix):
        response = requests.get(self.url + url_postfix, params=self.params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            print("Server error: 500")
            exit(1)
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            exit(1)

    def get_position(self, car, only_last=True):
        request_url = f"/status/{car['company_name']}/{car['car_name']}"
        car_status_json = self.__send_request(request_url)
        if only_last:
            for device in car_status_json[::-1]:
                device_id = device.get('device_id', {})
                if device_id.get('name') == 'virtual_vehicle':
                    position = device.get('payload', {}).get('data', {}).get('telemetry', {}).get('position', {})
                    return [{'lat': position.get('latitude'), 'lon': position.get('longitude')}]
        else:
            positions = []
            for device in car_status_json:
                device_id = device.get('device_id', {})
                if device_id.get('name') == 'virtual_vehicle':
                    position = device.get('payload', {}).get('data', {}).get('telemetry', {}).get('position', {})
                    positions.append({'lat': position.get('latitude'), 'lon': position.get('longitude')})
            return positions

    def get_positions(self, only_last=True):
        cars_json = self.__send_request("/cars")
        cars_positions = {}
        for car in cars_json:
            positions = self.get_position(car, only_last)
            if positions:
                car_key = f"{car['company_name']}/{car['car_name']}"
                cars_positions[car_key] = positions
        return cars_positions
