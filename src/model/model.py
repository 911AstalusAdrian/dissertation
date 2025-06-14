import fastf1
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# if it's stupid but it works, it ain't stupid

from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from scipy.stats import linregress

from src.utils.cache import DRIVERS_2018, DRIVERS_2019, DRIVERS_2020, DRIVERS_2021, DRIVERS_2022
from src.data_ingestion.fastf1_loader import get_synergy_metrics, get_synergy_metrics_for_drivers
from src.data_ingestion.openf1_loader import get_drivers_for_season

def compute_synergy_score(metrics: dict) -> float:
    score = (
        -metrics['Teammate_delta'] * 2 +  # negative delta = faster than teammate
        -metrics['Lap_stdev'] * 1.5 +     # lower std dev = more consistent
        -metrics['Avg_Q'] * 0.5 +         # higher qual = better driver performance
        -metrics['Avg_R'] * 1.0 +         # higher race position = better result
        -metrics['DNFRate'] * 3           # fewer DNFs = more reliable
    )
    return score

def compute_historic_synergies():
    driver_season_data = []
    for season in [2023, 2024]:
        print(f'PROCESSING YEAR {season}')
        drivers = get_drivers_for_season(season)
        for driver in drivers:
            try:
                print(f'Calculating synergy for {driver} in {season}')
                driver_metrics = get_synergy_metrics(driver, season)
                synergy_score = compute_synergy_score(driver_metrics)
                driver_season_data.append({
                    'Driver': driver,
                    'Season': season,
                    'Teammate_delta': driver_metrics['Teammate_delta'],
                    'Lap_stdev': driver_metrics['Lap_stdev'],
                    'Avg_Q': driver_metrics['Avg_Q'],
                    'Avg_R': driver_metrics['Avg_R'],
                    'DNFRate': driver_metrics['DNFRate'],
                    'SynergyScore': synergy_score
                })
            except Exception as e:
                print(f'Skipping driver {driver} from {season}: {str(e)}')

    # driver_synergy_data_df = pd.DataFrame(driver_season_data)
    # driver_synergy_data_df.to_csv('historic_data.csv')

def compute_synergies_for_season():
    driver_season_data = []
    drivers = DRIVERS_2022
    season = 2022
    try:
        synergy_metrics = get_synergy_metrics_for_drivers(drivers, season)
        for driver in drivers:
            driver_metrics = synergy_metrics.get(driver)
            synergy_score = compute_synergy_score(driver_metrics)
            driver_season_data.append({
                'Driver': driver,
                'Season': season,
                'Teammate_delta': driver_metrics['Teammate_delta'],
                'Lap_stdev': driver_metrics['Lap_stdev'],
                'Avg_Q': driver_metrics['Avg_Q'],
                'Avg_R': driver_metrics['Avg_R'],
                'DNFRate': driver_metrics['DNFRate'],
                'SynergyScore': synergy_score
            })
        driver_synergy_data_df = pd.DataFrame(driver_season_data)
        driver_synergy_data_df.to_csv('historic_data_2021.csv')
    except Exception as e:
        print(str(e))

compute_synergies_for_season()


# for year in range(2020, 2025):
#     df = pd.read_csv(f'data\\historic_synergies\\historic_data_{year}.csv')
#     print(df.head())
