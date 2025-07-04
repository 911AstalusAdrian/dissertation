# Responsible for loading data from the OpenF1 API

import requests
import pandas as pd
import time

BASE_URL = 'https://api.openf1.org/v1/'

def fetch_openf1_data(endpoint: str, params: dict = {}) -> pd.DataFrame:
    all_data = []
    limit = 10000
    offset = 0

    while True:
        response = requests.get(BASE_URL + endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        if not data: 
            break

        all_data.extend(data)
        offset += limit

    return pd.DataFrame(all_data)

def fetch_static_data(endpoint: str, params: dict = {}) -> pd.DataFrame:
    data = []
    response = requests.get(BASE_URL + endpoint, params=params)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data)

### Sessions calls

def get_last_session() -> str:
    df = fetch_static_data("sessions")
    latest_session = df.sort_values("session_key", ascending=False).iloc[0]["session_key"]
    return str(latest_session)

def get_sessions(circuit_key=None, meeting_key=None, session_key=None, session_name=None, session_type=None, year=None):
    params = {"circuit_key": circuit_key,
              "meeting_key": meeting_key,
              "session_key": session_key,
              "session_name": session_name,
              "session_type": session_type,
              "year": year}
    return fetch_static_data("sessions", params)

def get_sessions_list(circuit_key=None, meeting_key=None, session_key=None, session_name = None, session_type=None, year=None):
    params = {'circuit_key': circuit_key,
              'meeting_key': meeting_key,
              'session_key': session_key,
              'session_name': session_name,
              'session_type': session_type,
              'year': year}
    all_sessions = fetch_static_data('sessions', params)
    return all_sessions['session_key'].to_list()

def get_sessions_count():
    return get_sessions()['session_key'].count()

def get_races_per_season(season=2023):
    params = {'year': season}
    season_sessions = fetch_static_data('sessions', params)

    grouped = (
    season_sessions.groupby('circuit_short_name')['session_name']
    .apply(lambda x: sorted(set(x), key=lambda y: y.lower()))
    .to_dict()
    )

    return grouped

### Drivers calls

def get_distinct_drivers(country_code=None, driver_number=None, meeting_key=None, session_key=None, team_name=None):
    params = {'country_code': country_code,
              'driver_number': driver_number,
              'meeting_key': meeting_key,
              'session_key': session_key,
              'team_name': team_name}
    all_drivers =  fetch_static_data('drivers', params)
    unique_drivers = all_drivers.drop_duplicates(subset='full_name')
    return unique_drivers # returns the entire dataframe

def get_distinct_drivers_list(country_code=None, driver_number=None, meeting_key=None, session_key=None, team_name=None):
    params = {'country_code': country_code,
            'driver_number': driver_number,
            'meeting_key': meeting_key,
            'session_key': session_key,
            'team_name': team_name}
    all_drivers =  fetch_static_data('drivers', params)
    unique_drivers = all_drivers.drop_duplicates(subset='full_name')
    return unique_drivers

def get_fulltime_drivers():
    unique_drivers = get_distinct_drivers()

    for index, driver in unique_drivers.iterrows():
        
        if driver['first_name'] is None and driver['last_name'] is None:
            if driver['full_name'] != 'Gabriel BORTOLETO':
                unique_drivers.drop(index, inplace=True)
            continue
        try:
            composed_name = driver['first_name'] + ' ' + driver['last_name'].upper()

            if driver['full_name'] != composed_name:
                if driver['full_name'] == 'ZHOU Guanyu' and composed_name == 'Guanyu ZHOU':
                    continue
                
                unique_drivers.drop(index, inplace=True)

        except Exception as e:
            print(f'Error: {e}')
            continue

    unique_drivers.loc[unique_drivers.full_name == 'Gabriel BORTOLETO', ['first_name', 'last_name']] = 'Gabriel', 'Bortoleto'
    return unique_drivers

def get_distinct_drivers_count():
    return get_distinct_drivers()['full_name'].count()

def get_driver(driver_number=None, session_key=None):
    params = {"driver_number":driver_number, "session_key": session_key}
    return fetch_static_data("drivers", params)

def get_driver_image(full_name: str = None) -> str:

    # add try catch block for drivers without picture
    # cases: 1. API call returns nothing ( [] )
    #        2. The headshot_url is not availavble at all
    #        3. The headshot_url is not available on the first api response JSON

    name = full_name.split(' ')
    if len(name) < 3:
        params = {'first_name': name[0], 'last_name': name[1]}
    else:
        params = {'first_name': f'{name[1]} {name[0]}', 'last_name': name[2]}

    # print(params)
    result = fetch_static_data('drivers', params)
    return result.iloc[10]['headshot_url']

def get_recent_drivers(start_year:int = 2023, end_year:int = 2025):

    distinct_drivers = set()

    for each_year in range(start_year, end_year+1):
        year_races = get_sessions_list(session_name='Race', year=each_year)
        print(f'Got sessions for {each_year}')
        for each_race in year_races:
            race_drivers = get_distinct_drivers(session_key=each_race)
            print(f'Got drivers for session {each_race}')
            time.sleep(1)
            race_drivers['FullName'] = race_drivers['first_name'] + ' ' + race_drivers['last_name']
            race_drivers_list = race_drivers['FullName'].to_list()
            for driver in race_drivers_list: distinct_drivers.add(driver)
    return distinct_drivers

def get_drivers_for_season(season:int = 2025):
    drivers_per_season = set()
    races = get_sessions_list(session_name='Race', year=season)
    for each_race in races:
        race_drivers = get_distinct_drivers(session_key=each_race)
        time.sleep(1)
        race_drivers['FullName'] = race_drivers['first_name'] + ' ' + race_drivers['last_name']
        race_drivers_list = race_drivers['FullName'].to_list()
        for driver in race_drivers_list: drivers_per_season.add(driver)

    return list(drivers_per_season)
### Laps calls

def get_laps(driver_number=None, lap_number=None, meeting_key=None, session_key=None):
    params = {'session_key':session_key,
              'lap_number': lap_number,
              'meeting_key': meeting_key,
              'session_key': session_key}
    return fetch_static_data('laps', params)

def get_laps_count():
    total_laps = 0
    sessions_list = get_sessions_list()

    for session_key in sessions_list:
        session_laps = get_laps(session_key=session_key)
        total_laps += (len(session_laps))

    return total_laps

### Other calls

def get_car_data(session_key=None, driver_number=None):
    params = {"session_key": session_key, "driver_number": driver_number}
    return fetch_openf1_data("car_data", params)

def get_teams_for_driver(driver_name=None):
    params = {'full_name': driver_name}

    driver_rows = fetch_static_data('drivers' ,params)
    unique_teams = driver_rows.drop_duplicates(subset='team_name')

    return unique_teams['team_name'].to_list()


def get_teams_for_season(season:int=2023):
    params = {'year': season}
    sessions = fetch_static_data('sessions', params)
    first_session_key = sessions.loc[0].session_key
    drivers = get_distinct_drivers(session_key=first_session_key)
    return list(set(drivers['team_name']))


# print(get_teams_for_season(2025))