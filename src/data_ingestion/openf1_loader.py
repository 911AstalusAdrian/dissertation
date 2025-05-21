# Responsible for loading data from the OpenF1 API

import requests
import pandas as pd

BASE_URL = 'https://api.openf1.org/v1/'

def fetch_openf1_data(endpoint: str, params: dict = {}) -> pd.DataFrame:
    all_data = []
    limit = 10000
    offset = 0

    while True:
        # params.update({"limit": limit, "offset": offset})
        response = requests.get(BASE_URL + endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        print(data)
        if not data: 
            break

        all_data.extend(data)
        offset += limit

    return pd.DataFrame(all_data)

def get_laps(year=2023, session_key=None, driver_number=None):
    params = {"session_key": session_key, "driver_number": driver_number, "year": year}
    return fetch_openf1_data("laps", params)

def get_car_data(session_key=None, driver_number=None):
    params = {"session_key": session_key, "driver_number": driver_number}
    return fetch_openf1_data("car_data", params)

def get_driver(driver_number=None, session_key=None):
    params = {"driver_number":driver_number, "session_key": session_key}
    return fetch_openf1_data("drivers", params)