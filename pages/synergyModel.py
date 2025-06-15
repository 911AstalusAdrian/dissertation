import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from src.data_ingestion.openf1_loader import get_drivers_for_season
from src.data_ingestion.fastf1_loader import get_synergy_metrics
from src.model.model import get_weights, set_weights
from src.utils.plot_utils import DRIVER_SYNERGY_COLOR, BEST_SYNERGY_COLOR, AVG_SYNERGY_COLOR

@st.cache_data
def get_historic_synergies():
    data = pd.read_csv(r"data/historic_synergies/normalised_synergies.csv")
    bins = [0, 30, 50, 70, 85, 100]
    labels = ['Very Poor', 'Poor', 'Moderate', 'Good', 'Excellent']
    data['SynergyLevel'] = pd.cut(data['SynergyScore'], bins=bins, labels=labels, right=True)
    return data

def plot_synergy_level_distribution(synergy_df):
    synergy_counts = synergy_df['SynergyLevel'].value_counts().sort_index()
    df = synergy_counts.reset_index()
    df.columns = ['SynergyLevel', 'Count']
    df = df.set_index('SynergyLevel')
    st.bar_chart(df)

def first_last_initials(full_name):
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0][0].upper()
    return parts[0][0].upper() + parts[-1][0].upper()

def plot_top_synergies(synergy_df, top=10):
    top_synergies = synergy_df.nlargest(top, 'SynergyScore')
    top_synergies['Initials'] = top_synergies['Driver'].apply(first_last_initials)
    top_synergies['DriverSeason'] = top_synergies['Initials'] + ' (' + top_synergies['Season'].astype(str) + ')'
    top_synergies = top_synergies.set_index('DriverSeason')
    st.bar_chart(top_synergies[['SynergyScore']], horizontal=True)

def get_latest_season_drivers():
    latest_season = datetime.today().year
    drivers_list = get_drivers_for_season(latest_season)
    return drivers_list

def plot_driver_synergies(driver, data):
    avg_synergy = data.groupby('Season')['SynergyScore'].mean().rename('Average')
    max_synergy = data.groupby('Season')['SynergyScore'].max().rename('Best')
    driver_synergy = data[data['Driver'] == driver].set_index('Season')['SynergyScore'].rename(driver)


    synergy_plot_df = pd.concat([driver_synergy, avg_synergy, max_synergy], axis=1)
    synergy_plot_df = synergy_plot_df.sort_index()
    st.line_chart(synergy_plot_df, color=[DRIVER_SYNERGY_COLOR, AVG_SYNERGY_COLOR, BEST_SYNERGY_COLOR])


drivers_list = get_latest_season_drivers()
data = get_historic_synergies() 
driver = st.sidebar.selectbox('Pick a driver', options=drivers_list)
show_model_stats = st.sidebar.button('Show model stats')

def show_weights():
    weights = get_weights()
    weight_metrics = list(weights.keys())
    cols = st.columns(len(weight_metrics))
    for index, metric in enumerate(weight_metrics):
        cols[index].metric(metric, weights[metric])

if show_model_stats:
    st.dataframe(data)
    show_weights()
    plot_col1, plot_col2 = st.columns([1,2])
    with plot_col1:
        st.markdown('Distribution of synergy levels over the dataset')
        plot_synergy_level_distribution(data)
    with plot_col2:
        st.markdown('Top ten synergy levels from the dataset')
        plot_top_synergies(data, top=10)
    
    st.markdown('Driver Synergy levels compared to the best and average over the seasons')
    plot_driver_synergies(driver, data)
