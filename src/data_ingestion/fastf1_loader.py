# Responsible for loading the data from the FastF1 Python package
import fastf1
import pandas as pd
import numpy as np
import time

from datetime import timedelta
from datetime import datetime



def format_laptime(td:timedelta) -> str:

    if td is not None: 
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = int(td.microseconds / 1000)

        return f'{minutes}:{seconds:02d}:{milliseconds:03d}'
    
    else: return None

def format_session_type(session_type):
    session_type_formatted = None
    match session_type:
        case 'Practice 1':
            session_type_formatted = 'FP1'
        case 'Practice 2':
            session_type_formatted = 'FP2'
        case 'Practice 3':
            session_type_formatted = 'FP3'
        case _:
            session_type_formatted = session_type

    return session_type_formatted

def load_session_data(season, round_name, session_type):

    session_type_formatted = format_session_type(session_type)
    try:
        session = fastf1.get_session(season, round_name, session_type_formatted)
        session.load()
        return session
    except Exception as e:
        print(f'Error loading session: {e}')
        return None
    
def get_kpis_from_session(season, selected_round, session_type):

    session = load_session_data(season, selected_round, session_type)

    if session is None:
        return None
    try:
        laps = session.laps

        fastest = laps.pick_fastest()
        fastest_driver = fastest['Driver']
        fastest_lap = fastest['LapTime']
        fastest_lap_number = fastest['LapNumber']
        fastest_lap_compound = fastest['Compound']

        total_laps = len(laps)

        laps_per_driver = laps['Driver'].value_counts()
        top_driver = laps_per_driver.idxmax()
        max_laps = laps_per_driver.max()

        laps_per_team = laps['Team'].value_counts()
        print(laps_per_team)
        top_team = laps_per_team.idxmax()
        max_laps_team = laps_per_team.max()

        result = {
            'fastest_driver': fastest_driver,
            'fastest_lap': fastest_lap,
            'fastest_lap_number': fastest_lap_number,
            'fastest_lap_compound': fastest_lap_compound,
            'total_laps': total_laps,
            'top_driver': top_driver,
            'max_laps': max_laps,
            'top_team': top_team,
            'max_laps_team': max_laps_team
        }
        return result
    
    except Exception as e:
        print(f'Error extracting KPIs: {e}')
        return None

def get_session_top5_drivers_laps(season, selected_round, session_type):
    session = load_session_data(season, selected_round, session_type)

    top5_drivers = session.results[:5]['Abbreviation'].to_list()

    top5_laps = session.laps.pick_drivers(top5_drivers)
    top5_laps = top5_laps.dropna(subset=['LapTime'])
    top5_laps['LapTimeSeconds'] = top5_laps['LapTime'].dt.total_seconds()

    final_df = pd.DataFrame(top5_laps)
    return final_df[['LapTimeSeconds', 'LapNumber', 'Driver']]

def get_session_tyre_distribution(season, selected_round, session_type):
    session = load_session_data(season, selected_round, session_type)
    laps = session.laps
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    grouped_laps = laps.groupby('Compound')

    total_laps = (
        laps.groupby('Compound')
        .size()
        .reset_index(name='TotalLaps')
    )

    stint_lengths = (
    laps
    .groupby(['Compound', 'Driver', 'Stint'])
    .size()
    .reset_index(name='StintLength')
    )

    longest_stints = (
        stint_lengths
        .groupby('Compound')['StintLength']
        .max()
        .reset_index()
        .rename(columns={'StintLength': 'LongestIndividualStint'})
    )

    average_stints = (
        stint_lengths
        .groupby('Compound')['StintLength']
        .mean()
        .reset_index()
        .rename(columns={'StintLength' : 'AverageStintLength'})
    )

    fastest_laps = (
        grouped_laps['LapTimeSeconds']
        .min()
    )

    average_laps = (
        grouped_laps['LapTimeSeconds']
        .mean()
    )

    compound_summary = (
    total_laps
    .merge(longest_stints, on='Compound')
    .merge(average_stints, on='Compound')
    .merge(fastest_laps, on='Compound')
    .merge(average_laps, on='Compound')
    )

    compound_summary.rename(columns={'LapTimeSeconds_x' : 'FastestLapTime',
                                     'LapTimeSeconds_y' : 'AverageLapTime'},
                            inplace=True)

    return compound_summary

def get_distinct_drivers(first_season = 2018, last_season = 2025):

    all_drivers = set()

    for season in range(last_season, first_season - 1, -1):
        try:
            schedule = fastf1.get_event_schedule(season)
        except Exception as e:
            print(f'Skipping season {season}: {e}')

        print(f'Processing season {season}...')

        season_opener = fastf1.get_event(season, 1)
        season_opener_race = season_opener.get_race()
        season_opener_race.load(telemetry=False, weather=False, messages=False, livedata=False)
        drivers = season_opener_race.results['FullName']
        all_drivers.update(drivers)

    return sorted(all_drivers)

def get_driver_stats_multiseason(driver_full_name: str, start_year: int = 2018, end_year: int = None) -> dict:
    if end_year is None:
        end_year = datetime.now().year

    stats = {
        'Name': driver_full_name,
        'Races': 0,
        'Finished': 0,
        'DNFs': 0,
        'Wins': 0,
        'Podiums': 0,
        'Points': 0.0,
        'Teams': set()
    }

    for year in range(start_year, end_year + 1):
        try:
            schedule = fastf1.get_event_schedule(year)
        except Exception as e:
            print(f"Skipping year {year}: {e}")
            continue

        for _, row in schedule.iterrows():
            if row['Session5'] != 'Race':
                continue  # Only care about race sessions

            try:
                session = fastf1.get_session(year, row['EventName'], 'R')
                session.load(telemetry=False, weather=False, messages=False, livedata=False)
                time.sleep(1)
                results = session.results
                if results is None or results.empty:
                    continue

                driver_row = results[results['FullName'] == driver_full_name]
                if driver_row.empty:
                    continue

                dr = driver_row.iloc[0]

                stats['Races'] += 1
                stats['Points'] += dr.get('Points', 0.0) or 0.0
                stats['Teams'].add(dr['TeamName'])

                if isinstance(dr['Status'], str) and 'Finished' in dr['Status']:
                    stats['Finished'] += 1
                else:
                    stats['DNFs'] += 1

                if dr['Position'] == 1:
                    stats['Wins'] += 1
                    stats['Podiums'] += 1
                elif dr['Position'] in [2, 3]:
                    stats['Podiums'] += 1

            except Exception as e:
                print(f"Failed to process race {row['EventName']} in {year}: {e}")
                continue

            # time.sleep(1)

    stats['Points'] = round(stats['Points'], 1)
    stats['Avg Points/Race'] = round(stats['Points'] / stats['Races'], 2) if stats['Races'] > 0 else 0.0
    stats['Teams'] = sorted(stats['Teams'])

    return stats

def get_events_for_season(season:int = 2025):
    schedule = fastf1.get_event_schedule(season)

    # cleaning the schedule (remove testing and keep only completed events for current year)
    for index, event in schedule.iterrows():
        if event['EventFormat'] == 'testing':
            # print(f'Removing {event["EventName"]} - testing session')
            schedule.drop(index, inplace=True)
        if event['EventDate'] > datetime.today():
            # print(f'Removing {event["EventName"]} - in the future')
            schedule.drop(index, inplace=True)

    return schedule

def get_event_names_for_season(season:int = 2025):
    schedule = get_events_for_season(season)
    return schedule['EventName']

def get_average_quali_pos(driver:str = None, season:int = 2025, season_races:list = []):
    
    quali_results_for_driver = []

    for race in season_races:

        # Load quali session
        quali = fastf1.get_session(season, race, 'Q')
        quali.load()
        
        quali_results = quali.results
        for index, row in quali_results.iterrows():
            if row['FullName'].lower() == driver.lower():
                quali_results_for_driver.append(row['Position'])

    return sum(quali_results_for_driver) / len(quali_results_for_driver)
                
def get_race_results_over_seasons(driver:str = None, starting_season:int = 2018, last_season:int = 2025):

    driver_results = []

    for year in range(starting_season, last_season + 1):
        schedule = get_events_for_season(year)
        for _, event in schedule.iterrows():
            try:
                # Get and Load race results
                race = event.get_race()
                race.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
                race_results = race.results

                # Error handling in case results is empty
                if race_results is None or race_results.empty:
                    continue

                # Get race result for a specific driver + error handling
                driver_result = race_results.loc[race_results['FullName'] == driver]
                if driver_result is None or driver_result.empty:
                    continue

                dr = driver_result.iloc[0]
                driver_results.append({
                    'Season': year,
                    'RaceName': event['EventName'],
                    # 'FullName': dr['FullName'],
                    'TeamName': dr['TeamName'],
                    'Position': dr['Position'],
                    'Points': dr['Points']
                })
            except Exception as e:
                print(f'Error in {event['EventName']} - {year}: {e}')
                continue


    driver_results_df = pd.DataFrame(driver_results)
    return driver_results_df

def calculate_quali_teammate_delta(driver_res, teammate_res):
    if not pd.notna(driver_res['Q3']):
        if not pd.notna(driver_res['Q2']):
            if not pd.notna(driver_res['Q1']):
                driver_best_time = 0
            else: 
                driver_best_time = driver_res['Q1']
        else:
            driver_best_time = driver_res['Q2']
    else:
        driver_best_time = driver_res['Q3']

    if not pd.notna(teammate_res['Q3']):
        if not pd.notna(teammate_res['Q2']):
            if not pd.notna(teammate_res['Q1']):
                teammate_best_time = 0
            else:
                teammate_best_time = teammate_res['Q1']
        else:
            teammate_best_time = teammate_res['Q2']
    else:
        teammate_best_time = teammate_res['Q3']

    if driver_best_time == 0 or teammate_best_time == 0:
        delta = timedelta(seconds=0)
    else:
        delta = driver_best_time - teammate_best_time
    # print(f'{delta_seconds:.3f}')
    delta_seconds = delta.total_seconds()

    if abs(delta_seconds ) > 5: return 0.0
    return delta_seconds

def calculate_race_teammate_h2h(driver_res, teammate_res):
    return driver_res['Position'] - teammate_res['Position']

def get_driver_teammate_comparison_over_seasons(driver:str = None, starting_season:int = 2018, last_season:int = 2025):

    teammate_comparisons = []

    for year in range(starting_season, last_season + 1):
        print(f'YEAR IS: {year}')
        quali_count = 0
        quali_delta = 0
        quali_for = 0
        quali_against = 0
        race_for = 0
        race_against = 0
        sessions = get_events_for_season(year)
        for _, session in sessions.iterrows():

            try:
                # Race H2H calculations
                race = session.get_race()
                race.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
                race_results = race.results

                driver_race_res = race_results.loc[race_results['FullName'] == driver]
                driver_race_res = driver_race_res.iloc[0]

                team_name = driver_race_res['TeamId']
                
                teammate_race_res = race_results.loc[(race_results['TeamId'] == team_name) & (race_results['FullName'] != driver)]
                teammate_race_res = teammate_race_res.iloc[0]

                teammate_pos_diff = calculate_race_teammate_h2h(driver_race_res, teammate_race_res)
                if teammate_pos_diff < 0: race_for += 1
                else: race_against += 1

                time.sleep(0.5)

                # Qualifying H2H calculations
                quali = session.get_qualifying()
                quali.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
                quali_results = quali.results

                driver_quali_res = quali_results.loc[quali_results['FullName'] == driver]
                driver_quali_res = driver_quali_res.iloc[0]

                teammate_quali_res = quali_results.loc[(quali_results['TeamId'] == team_name) & (quali_results['FullName'] != driver)]
                teammate_quali_res = teammate_quali_res.iloc[0]

                # Not taking into consideration weather changes during Quali (ex: Canada 2023)
                # For differences in delta > 5 we mark them with 0 (invalid quali)
                teammate_delta = calculate_quali_teammate_delta(driver_quali_res, teammate_quali_res)
                if teammate_delta != timedelta(seconds=0).total_seconds():
                    if teammate_delta > pd.Timedelta(0).total_seconds(): quali_against += 1
                    else: quali_for += 1
                    quali_count += 1
                    quali_delta += teammate_delta

            except Exception as e:
                print(f'ERROR! {year} {session['EventName']} - {repr(e)}')
                time.sleep(2)
                continue
        
        if quali_count != 0:
            teammate_comparisons.append({
                'Season': year,
                'QualiDelta': quali_delta / quali_count,
                'QualiFor': quali_for,
                'QualiAgainst': quali_against,
                'RaceFor': race_for,    
                'RaceAgainst': race_against
            })

    teammate_comparisons_df = pd.DataFrame(teammate_comparisons)
    return teammate_comparisons_df

# races = get_event_names_for_season(2025)
# print(get_average_quali_pos('Max VERSTAPPEN', 2025, races))
# print(get_race_results_over_seasons('Oscar Piastri', 2025, 2025))
# print(get_driver_teammate_comparison_over_seasons('Alexander Albon', 2018, 2025))