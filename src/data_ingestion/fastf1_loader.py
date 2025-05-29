# Responsible for loading the data from the FastF1 Python package
import fastf1

def load_session_data(season, round_name, session_type):
    try:
        session = fastf1.get_session(season, round_name, session_type)
        session.load()
        return session
    except Exception as e:
        print(f'Error loading session: {e}')
        return None
    
def get_kpis_from_session(season, session_type, selected_round):

    session = load_session_data(season, session_type, selected_round)

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
