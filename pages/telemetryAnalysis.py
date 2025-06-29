import fastf1
from datetime import datetime, timedelta
import pandas as pd
import time

DNF_STATUSES = {'Accident', 'Collision', 'Engine', 'Mechanical', 'Retired', 'Disqualified', 'DNF'}
FINISHED_STATUSES = {'Finished', 'Active', 'Running', 'Completed'}

def calculate_quali_teammate_delta(driver_quali_result, teammate_quali_result):
    # Example placeholder: compute difference in qualifying times in seconds
    # Adapt as needed to your real logic
    delta = driver_quali_result['Q3'] - teammate_quali_result['Q3']
    if pd.isna(delta) or abs(delta.total_seconds()) > 5:
        return 0  # Invalid delta
    return delta.total_seconds()

def get_driver_full_info(driver: str = None, starting_season: int = 2018, last_season: int = 2025):
    driver_info = {
        'TotalRaces': 0,
        'Finished': 0,
        'DNFs': 0,
        'Wins': 0,
        'Podiums': 0,
        'Points': 0,
        'Teams': set()
    }

    results = []
    teammate_comparisons = []

    for year in range(starting_season, last_season + 1):
        quali_count = 0
        quali_delta = 0
        quali_for = 0
        quali_against = 0
        race_for = 0
        race_against = 0

        schedule = None
        try:
            schedule = fastf1.get_event_schedule(year)
        except Exception as e:
            print(f'[Warning] Failed to get schedule for year {year}: {e}')
            continue  # Skip this year

        if schedule is None or schedule.empty:
            print(f'[Warning] No schedule found for year {year}. Skipping.')
            continue

        for _, event in schedule.iterrows():
            if event['EventFormat'] == 'testing':
                continue  # Skip testing sessions

            if event['EventDate'] > datetime.today():
                continue  # Skip future events

            try:
                event_race = event.get_race()
                event_race.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
            except Exception as e:
                print(f'[Warning] Failed to load race for {event["EventName"]} {year}: {e}')
                continue

            race_results = event_race.results
            driver_result = race_results.loc[race_results['FullName'] == driver]

            if driver_result.empty:
                print(f'[Info] Driver {driver} did not participate in {event["EventName"]} {year}')
                continue

            driver_result = driver_result.iloc[0]

            driver_info['TotalRaces'] += 1

            status = driver_result['Status']
            if status in DNF_STATUSES:
                driver_info['DNFs'] += 1
            if status in FINISHED_STATUSES:
                driver_info['Finished'] += 1

            position = driver_result['Position']
            if position == 1:
                driver_info['Wins'] += 1
            if 1 <= position <= 3:
                driver_info['Podiums'] += 1

            points = driver_result['Points']
            driver_info['Points'] += points

            team = driver_result['TeamName']
            driver_info['Teams'].add(team)

            results.append({
                'Season': year,
                'RaceName': event['EventName'],
                'TeamName': team,
                'Position': position,
                'Points': points
            })

            team_id = driver_result['TeamId']

            teammate_race_result = race_results.loc[(race_results['TeamId'] == team_id) & (race_results['FullName'] != driver)]
            if teammate_race_result.empty:
                print(f'[Info] No teammate for {driver} in race {event["EventName"]} {year}')
                continue

            teammate_race_result = teammate_race_result.iloc[0]
            race_diff = position - teammate_race_result['Position']
            if race_diff < 0:
                race_for += 1
            else:
                race_against += 1

            time.sleep(0.5)  # To avoid API overload

            try:
                event_quali = event.get_qualifying()
                event_quali.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
                quali_results = event_quali.results
            except Exception as e:
                print(f'[Warning] Failed to load qualifying for {event["EventName"]} {year}: {e}')
                continue

            driver_quali_result = quali_results.loc[quali_results['FullName'] == driver]
            if driver_quali_result.empty:
                print(f'[Info] Driver {driver} did not participate in qualifying for {event["EventName"]} {year}')
                continue

            driver_quali_result = driver_quali_result.iloc[0]

            teammate_quali_result = quali_results.loc[(quali_results['TeamId'] == team_id) & (quali_results['FullName'] != driver)]
            if teammate_quali_result.empty:
                print(f'[Info] No teammate qualifying for {driver} in {event["EventName"]} {year}')
                continue

            teammate_quali_result = teammate_quali_result.iloc[0]

            teammate_delta = calculate_quali_teammate_delta(driver_quali_result, teammate_quali_result)

            if teammate_delta != 0:
                if teammate_delta > 0:
                    quali_against += 1
                else:
                    quali_for += 1
                quali_count += 1
                quali_delta += teammate_delta

        if quali_count > 0:
            teammate_comparisons.append({
                'Season': year,
                'QualiDelta': quali_delta / quali_count,
                'QualiFor': quali_for,
                'QualiAgainst': quali_against,
                'RaceFor': race_for,
                'RaceAgainst': race_against
            })

    results_df = pd.DataFrame(results)
    comparisons_df = pd.DataFrame(teammate_comparisons)

    driver_info['Results'] = results_df
    driver_info['Comparisons'] = comparisons_df

    return driver_info
