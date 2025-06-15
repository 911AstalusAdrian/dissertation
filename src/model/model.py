import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# if it's stupid but it works, it ain't stupid

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from sklearn.preprocessing import MinMaxScaler

from src.data_ingestion.fastf1_loader import get_synergy_metrics, get_synergy_metrics_for_drivers
from src.data_ingestion.openf1_loader import get_drivers_for_season

weights = {
    'Teammate_delta': 2.0,
    'Lap_stdev': 1.5,
    'Avg_Q': 0.5,
    'Avg_R': 1.0,
    'DNFRate': 3.0
}

def compute_synergy_score(metrics: dict) -> float:
    score = (
        -metrics['Teammate_delta'] * weights['Teammate_delta'] +  # negative delta = faster than teammate
        -metrics['Lap_stdev'] * weights['Lap_stdev'] +     # lower std dev = more consistent
        -metrics['Avg_Q'] * weights['Avg_Q'] +         # higher qual = better driver performance
        -metrics['Avg_R'] * weights['Avg_R'] +         # higher race position = better result
        -metrics['DNFRate'] * weights['DNFRate']           # fewer DNFs = more reliable
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
    drivers = None  # Manually load drivers list
    season = None   # Manually input season to mach drivers list
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

def data_cleaning(dataframe):
    # read each csv as a dataframe and concatenate it to the initial dataframe
    for year in range(2020, 2025):
        df = pd.read_csv(f'data\\historic_synergies\\historic_data_{year}.csv')
        dataframe = pd.concat([dataframe, df])

    dataframe = dataframe.dropna(subset=['SynergyScore']) # Remove invalid Synergy scores
    dataframe = dataframe.loc[dataframe['SynergyScore'] != 0] # Remove rows with Synergy Score 0 (most likely errors)
    dataframe = dataframe.loc[dataframe['Avg_Q'] != 0] # Remove Qualifying outliers
    # It is not necessary for the other columns, as there are no zero values (except for DNFRate, where it is possible to be 0)

    return dataframe

def get_weights():
    return weights

def set_weights(teammate_delta, lap_stdev, avg_q, avg_r, dnf_rate):
    weights['Teammate_delta'] = teammate_delta
    weights['Lap_stdev'] = lap_stdev
    weights['Avg_Q'] = avg_q
    weights['Avg_R'] = avg_r
    weights['DNFRate'] = dnf_rate

def model_features_importance(model, X):
    importances = model.feature_importances_
    features = X.columns

    indices = np.argsort(importances)[::-1]
    sorted_features = [features[i] for i in indices]
    sorted_importances = importances[indices]

    return sorted_features, sorted_importances

def train_model(dataframe):
    X = dataframe[['Teammate_delta', 'Lap_stdev', 'Avg_Q', 'Avg_R', 'DNFRate']]
    y = dataframe['SynergyScore']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    print("Test RMSE: ", root_mean_squared_error(y_test, predictions))
    print(y_test)
    print(predictions)

def recalculate_synergy():
    for year in range(2020, 2025):
        df = pd.read_csv(f'data\\historic_synergies\\historic_data_{year}.csv')
        for index, driver in df.iterrows():
            metrics = driver[['Teammate_delta', 'Lap_stdev', 'Avg_Q', 'Avg_R', 'DNFRate']]
            new_syn = compute_synergy_score(metrics)
            df.loc[index, 'SynergyScore'] = new_syn
        df.to_csv(f'data\\historic_synergies\\historic_data_{year}.csv', index=False) # update the CSV file

    normalised_df = pd.DataFrame()
    normalised_df = data_cleaning(normalised_df)[['Driver', 'Season', 'SynergyScore']]
    scaler = MinMaxScaler(feature_range=(0, 100))
    normalised_df['SynergyScore'] = scaler.fit_transform(normalised_df[['SynergyScore']]) 
    normalised_df.to_csv(f'data\\historic_synergies\\normalised_synergies.csv', index=False)

def set_weights_and_update_synergy(weights_list):
    set_weights(weights_list[0], weights_list[1], weights_list[2], weights_list[3], weights_list[4])
    recalculate_synergy()

# set_weights_and_update_synergy([1.0, 2.0, 0.5, 1.5, 0.5])
# recalculate_synergy()
# # ,Driver,Season,Teammate_delta,Lap_stdev,Avg_Q,Avg_R,DNFRate,SynergyScore
# df = pd.DataFrame()
# clean_df = data_cleaning(df)
# train_model(clean_df)