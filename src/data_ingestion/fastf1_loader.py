# Responsible for loading the data from the FastF1 Python package
import fastf1
import fastf1.plotting
import pandas as pd
from datetime import timedelta

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
    driver_rows = []

    for season in range(last_season, first_season - 1, -1):
        try:
            schedule = fastf1.get_event_schedule(season)
        except Exception as e:
            print(f'Skipping season {season}: {e}')

        print(f'Processing season {season}...')

        season_opener = fastf1.get_event(season, 1)
        season_opener_race = season_opener.get_race()
        season_opener_race.load(telemetry=False, weather=False, messages=False, livedata=False)
        drivers = season_opener_race.results[['Abbreviation', 'FullName', 'HeadshotUrl']]
        driver_rows.append(drivers)


        all_drivers = pd.concat(driver_rows).drop_duplicates(subset=['FullName', 'Abbreviation']).sort_values('FullName').reset_index(drop=True)
        all_drivers['DisplayName'] = all_drivers['FullName'] + ' (' + all_drivers['Abbreviation'] + ')'
    
    
    
    return all_drivers

# print(get_session_tyre_distribution(2025, 'Sakhir', 'Practice 1'))
# print(get_distinct_drivers())