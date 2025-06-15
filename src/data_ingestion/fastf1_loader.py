# Responsible for loading the data from the FastF1 Python package
import fastf1
import pandas as pd
import time

from datetime import timedelta, datetime

DNF_STATUSES = ['Collision damage', 'Hydraulics', 'Radiator', 'Collision', 'Retired', 'Did not start', 'Mechanical', 'Electronics']
FINISHED_STATUSES = ['+2 Laps', 'Lapped', 'Finished', '+1 Lap']

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
    delta_seconds = delta.total_seconds()

    if abs(delta_seconds ) > 5: return 0.0
    return delta_seconds

def get_driver_full_info(driver:str = None, starting_season:int = 2018, last_season:int = 2025):
    driver_info = {
        'TotalRaces' : 0,
        'Finished': 0,
        'DNFs': 0,
        'Wins': 0,
        'Podiums': 0,
        'Points': 0,
        'Teams': set()
    }

    results = []
    teammate_comparisons = []

    for year in range(starting_season, last_season+1):
        quali_count = 0
        quali_delta = 0
        quali_for = 0
        quali_against = 0
        race_for = 0
        race_against = 0
        try:
            schedule = fastf1.get_event_schedule(year)
        except Exception as e:
            print(f'Failed to get schedule for year {year}')
        for _, event in schedule.iterrows():
            # Skip over testing sessions
            if event['EventFormat'] == 'testing':
                continue

            # Skip over events in the future
            if event['EventDate'] > datetime.today():
                continue

            # Get the race event and load the results
            event_race = event.get_race()
            event_race.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
            race_results = event_race.results
            driver_result = race_results.loc[race_results['FullName'] == driver]

            # Skip events in which the driver was not part of the race
            if driver_result.empty:
                print('Driver did not participate in this event!')
                continue

            # Process general race stats
            driver_result = driver_result.iloc[0]

            driver_info['TotalRaces'] += 1 # Total Races

            # race status
            status = driver_result['Status']
            if status in DNF_STATUSES:
                driver_info['DNFs'] += 1 # DNF Races
            if status in FINISHED_STATUSES:
                driver_info['Finished'] += 1 # Finished Races

            # race position
            position = driver_result['Position']
            if position == 1:
                driver_info['Wins'] += 1 # Race Wins
            if position >= 1 and position <= 3:
                driver_info['Podiums'] += 1  # Race Podiums

            # total points
            points = driver_result['Points']
            driver_info['Points'] += points

            # team
            team = driver_result['TeamName']
            driver_info['Teams'].add(team)


            # driver results list
            team_name = driver_result['TeamName']
            results.append({
                'Season': year,
                'RaceName': event['EventName'],
                'TeamName': driver_result['TeamName'],
                'Position': position,
                'Points': points
            })

            # Calculate race H2H with teammate
            team_id = driver_result['TeamId'] # Team ID for better data gathering

            # Get the result of the teammate
            teammate_race_result = race_results.loc[(race_results['TeamId'] == team_id) & (race_results['FullName'] != driver)]
            if teammate_race_result.empty:
                print('Teammate did not participate in the race')
                continue
            teammate_race_result = teammate_race_result.iloc[0]

            # Compute race position delta
            race_diff = driver_result['Position'] - teammate_race_result['Position']
            if race_diff < 0 : race_for += 1
            else : race_against += 1

            time.sleep(0.5) # sleep to avoid overloading the API call

            # Load qualifying session
            event_quali = event.get_qualifying()
            event_quali.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
            quali_results = event_quali.results

            # Get driver quali result
            driver_quali_result = quali_results.loc[quali_results['FullName'] == driver]
            if driver_quali_result.empty:
                print('Driver did not participate in this Quali, but raced')
                continue
            driver_quali_result = driver_quali_result.iloc[0]

            # Get teammate quali result
            teammate_quali_result = quali_results.loc[(quali_results['TeamId'] == team_id) & (quali_results['FullName'] != driver)]
            if teammate_quali_result.empty:
                print('Teammate did not participate in this Quali, but raced')
                continue
            teammate_quali_result = teammate_quali_result.iloc[0]

            # Calculate quali delta
            teammate_delta = calculate_quali_teammate_delta(driver_quali_result, teammate_quali_result)
            # Invalid quali deltas are marked with 0 (teammate or driver did not take part in Q, or delta > 5s)
            # does not take into consideration weather changes (ex: Canada 2023)
            if teammate_delta != timedelta(seconds=0).total_seconds():
                if teammate_delta > pd.Timedelta(0).total_seconds() : quali_against += 1
                else: quali_for += 1
                quali_count += 1
                quali_delta += teammate_delta

        if quali_count != 0:
            teammate_comparisons.append({
                'Season': year,
                'QualiDelta': quali_delta / quali_count,
                'QualiFor': quali_for,
                'QualiAgainst': quali_against,
                'RaceFor': race_for,
                'RaceAgainst': race_against
            })    


    results_df = pd.DataFrame(results)
    driver_info['Results'] = results_df

    comparisons_df = pd.DataFrame(teammate_comparisons)
    driver_info['Comparisons'] = comparisons_df
    return driver_info

def compute_lap_deviation(laps, driver):
    # Get laps for the selected driver
    driver_laps = laps.pick_drivers(driver)

    # Convert laptime from Timedelta to seconds
    driver_laps['LapTimeSeconds'] = driver_laps['LapTime'].dt.total_seconds()
    # Filter valid laps only (not in lap, out lap, and laptimes must be accurate)
    clean_laps = driver_laps[
        driver_laps['PitInTime'].isnull() & 
        driver_laps['PitOutTime'].isnull() & 
        driver_laps['IsAccurate'] & 
        driver_laps['LapTime'].notnull()
    ]['LapTimeSeconds']
    if clean_laps.empty:
        return 0
    # Perform simple standard deviation
    laps_std = clean_laps.std()
    return laps_std

def compute_average_laptime(laps, driver_list):

    driver_averages = []

    for driver in driver_list:
        driver_laps = laps.pick_drivers(driver)
        driver_laps['LapTimeSeconds'] = driver_laps['LapTime'].dt.total_seconds()
        clean_laps = driver_laps[
        driver_laps['PitInTime'].isnull() & 
        driver_laps['PitOutTime'].isnull() & 
        driver_laps['IsAccurate'] & 
        driver_laps['LapTime'].notnull()
        ]['LapTimeSeconds']

        if clean_laps.empty:
            return [0 ,0]
        laps_avg = clean_laps.mean()
        driver_averages.append(laps_avg)
    return driver_averages

def get_synergy_metrics(driver:str = None, season:int = 2025):

    synergy_results = {}
    qualifying_positions = {}
    race_positions = {}
    lap_deltas = {}

    quali_pos = 0
    quali_count = 0

    race_count = 0
    race_sum = 0

    dnf_count = 0

    total_deviation = 0
    deviation_calculated_races = 0

    total_lap_delta = 0
    delta_calculated_races = 0
    driver_team_color = ''

    for round in range (1, 25):
        try:

            # Load Round's Qualifying
            quali = fastf1.get_session(season, round, 'Q')
            if quali.date > datetime.today():
                continue
            quali.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
            quali_results = quali.results # Get Quali results
            driver_quali = quali_results.loc[quali_results['FullName'] == driver] # Get Driver Quali data
            driver_quali = driver_quali.iloc[0]
            # Qualifying-related stats
            quali_pos += driver_quali['Position']   # add quali positions
            quali_count += 1                        # count qualifiers
            qualifying_positions[round] = int(driver_quali['Position']) # add quali pos to dict (for visualisations)
        except Exception as e:
            print(f'Error for quali round {round}: {str(e)}')

        try:
            # Load Round's Race
            race = fastf1.get_session(season, round, 'R')
            if race.date > datetime.today():
                continue
            race.load()
            race_results = race.results # Get Race results
            driver_race = race_results.loc[race_results['FullName'] == driver] # Get Driver Race data

            if driver_race.empty:
                continue

            driver_race = driver_race.iloc[0]
            # Race related stats
            race_pos = driver_race['Position']
            race_sum += race_pos
            # race_start = driver_race['GridPosition']
            race_status = driver_race['Status']
            race_positions[round] = int(race_pos)
            if race_status in DNF_STATUSES:
                dnf_count += 1
            race_count += 1

            driver_team_color = driver_race['TeamColor']

            # Compute race lap deviation
            laps = race.laps
            driver_abbr = driver_race['Abbreviation']
            lap_deviation = compute_lap_deviation(laps, driver_abbr)
            if lap_deviation != 0:
                total_deviation += lap_deviation
                deviation_calculated_races += 1

            # Compute race lap delta to teammate
            team_id = driver_race['TeamId']
            teammate_race = race_results.loc[(race_results['TeamId'] == team_id) & (race_results['FullName'] != driver)]
            if teammate_race.empty:
                print('No teammate raced')
                continue
            teammate_race = teammate_race.iloc[0]
            teammate_abbr = teammate_race['Abbreviation']

            driver_avg_lap, teammate_avg_lap = compute_average_laptime(laps, [driver_abbr, teammate_abbr])
            race_delta = driver_avg_lap - teammate_avg_lap
            if race_delta != 0:
                total_lap_delta += race_delta
                delta_calculated_races += 1
            lap_deltas[round] = race_delta

        except Exception as e:
            print(f'Error for race round {round}: {str(e)}')

    synergy_results['Teammate_delta'] = total_lap_delta / delta_calculated_races
    synergy_results['Lap_stdev'] = total_deviation/deviation_calculated_races
    synergy_results['Avg_Q'] = quali_pos/quali_count
    synergy_results['Avg_R'] = race_sum/race_count
    synergy_results['DNFRate'] = (dnf_count * 100) / race_count
    synergy_results['Q_positions'] = qualifying_positions
    synergy_results['R_positions'] = race_positions
    synergy_results['RaceLapDeltas'] = lap_deltas
    synergy_results['Color'] = driver_team_color

    return synergy_results

def get_synergy_metrics_for_drivers(drivers:list = [], season:int = 2025):
    
    drivers_synergies = {f'{driver}' : {
        'Teammate_delta': 0,
        'Lap_stdev': 0,
        'Avg_Q': 0,
        'Avg_R': 0,
        'DNFRate': 0,
        'total_lap_delta': 0,
        'delta_calculated_races': 0,
        'total_deviation': 0,
        'deviation_calculated_races': 0,
        'quali_pos': 0,
        'quali_count': 0,
        'race_sum': 0,
        'race_count': 0,
        'dnf_count': 0
    } for driver in drivers} 
    for round in range(1,25):
        try:
            quali = fastf1.get_session(season, round, 'Q')
            race = fastf1.get_session(season, round, 'R')
            if quali.date < datetime.today():
                quali.load(laps=False, telemetry=False, weather=False, messages=False, livedata=False)
                q_results = quali.results
                for driver in drivers:
                    driver_q = q_results.loc[q_results['FullName'] == driver] # Get Driver Quali data
                    if not driver_q.empty:
                        driver_q = driver_q.iloc[0]
                        driver_dict = drivers_synergies.get(driver)
                        driver_dict['quali_pos'] += driver_q['Position']
                        driver_dict['quali_count'] += 1
            
            if race.date < datetime.today():
                race.load()
                laps = race.laps
                r_results = race.results
                for driver in drivers:
                    driver_r = r_results.loc[r_results['FullName'] == driver]
                    if not driver_r.empty:
                        driver_r = driver_r.iloc[0]
                        driver_dict = drivers_synergies.get(driver)
                        driver_dict['race_sum'] += driver_r['Position']
                        race_status = driver_r['Status']
                        if race_status in DNF_STATUSES:
                            driver_dict['dnf_count'] += 1
                        driver_dict['race_count'] += 1

                        driver_abbr = driver_r['Abbreviation']
                        lap_deviation = compute_lap_deviation(laps, driver_abbr)
                        if lap_deviation != 0:
                            driver_dict['total_deviation'] += lap_deviation
                            driver_dict['deviation_calculated_races'] += 1

                        team_id = driver_r['TeamId']
                        teammate_r = r_results.loc[(r_results['TeamId'] == team_id) & (r_results['FullName'] != driver)]
                        if not teammate_r.empty:
                            teammate_r = teammate_r.iloc[0]
                            teammate_abbr = teammate_r['Abbreviation']
                            driver_avg_lap, teammate_avg_lap = compute_average_laptime(laps, [driver_abbr, teammate_abbr])
                            race_delta = driver_avg_lap - teammate_avg_lap
                            if race_delta != 0:
                                driver_dict['total_lap_delta'] += race_delta
                                driver_dict['delta_calculated_races'] += 1
        except Exception as e:
            print('Moving Forward')
            continue

    for driver in drivers:
        driver_dict = drivers_synergies.get(driver)
        if driver_dict['delta_calculated_races'] != 0:
            driver_dict['Teammate_delta'] = driver_dict['total_lap_delta'] / driver_dict['delta_calculated_races']
        if driver_dict['deviation_calculated_races'] != 0:
            driver_dict['Lap_stdev'] = driver_dict['total_deviation'] / driver_dict['deviation_calculated_races']
        if driver_dict['quali_count'] != 0:
            driver_dict['Avg_Q'] = driver_dict['quali_pos'] / driver_dict['quali_count']
        if driver_dict['race_count'] != 0: 
            driver_dict['Avg_R'] = driver_dict['race_sum'] / driver_dict['race_count']
            driver_dict['DNFRate'] = (driver_dict['dnf_count'] * 100) / driver_dict['race_count']

    return drivers_synergies

def compute_synergy_score(metrics: dict) -> float:
    score = (
        -metrics['Teammate_delta'] * 2.0 +      # negative delta = faster than teammate
        -metrics['Lap_stdev'] * 1.5 +           # lower std dev = more consistent
        -metrics['Avg_Q'] * 0.5 +               # higher qual = better driver performance
        -metrics['Avg_R'] * 1.0 +               # higher race position = better result
        -metrics['DNFRate'] * 3.0               # fewer DNFs = more reliable
    )
    return score

def get_driver_synergy_per_race(drivername:str=None, starting_season:int=2020, final_season:int=2025):
    drivername = 'Lewis Hamilton'
    driver_synergies = []
    for year in range(2021, 2025):
        events = fastf1.get_event_schedule(year)
        for race_index, event in events.iterrows():
            if event['EventFormat'] != 'testing':
                race = event.get_race()
                race.load()
                race_results = race.results
                driver_res = race_results.loc[race_results['FullName'] == drivername]
                if not driver_res.empty:

                    stats = {
                        'Teammate_delta' : 0,
                        'Lap_stdev': 0,
                        'Avg_Q': 0,
                        'Avg_R': 0,
                        'DNFRate': 0
                    }

                    driver_res = driver_res.iloc[0]
                    team_id = driver_res['TeamId']

                    teammate_res = race_results.loc[(race_results['TeamId'] == team_id) & (race_results['FullName'] != drivername)]
                    if teammate_res.empty:
                        continue
                    teammate_res = teammate_res.iloc[0]

                    teammate_abbr = teammate_res['Abbreviation']
                    driver_abbr = driver_res['Abbreviation']
                    race_laps = race.laps
                    driver_avg, teammate_avg = compute_average_laptime(race_laps, [driver_abbr, teammate_abbr])
                    driver_stdev = compute_lap_deviation(race_laps, driver_abbr)
                    stats['Lap_stdev'] = driver_stdev
                    race_delta = driver_avg - teammate_avg
                    if race_delta != 0:
                        stats['Teammate_delta'] = race_delta
                    stats['Avg_Q'] = driver_res['GridPosition']
                    stats['Avg_R'] = driver_res['Position']
                    if driver_res['Status'] in DNF_STATUSES: stats['DNFRate'] = 1
                    else: stats['DNFRate'] = 0

                    synergy = compute_synergy_score(stats)
                    stats['Season'] = year
                    stats['Round'] = race_index
                    stats['Synergy'] = synergy
                    driver_synergies.append(stats)
    return driver_synergies
