# Responsible for loading the data from the FastF1 Python package
import fastf1
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

    return top5_laps[['LapTime', 'LapNumber', 'Driver']]

def get_session_laptimes(season, selected_round, session_type):
    # WIP
    session = load_session_data(season, selected_round, session_type)
    laps = session.results[:5]['Abbreviation']
    return laps


print(get_session_top5_drivers_laps(2025, 'Sakhir', 'Practice 1'))