import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from src.data_ingestion.openf1_loader import get_drivers_for_season
from src.data_ingestion.fastf1_loader import get_synergy_metrics

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

def plot_driver_synergies(selected_driver, df):
    seasons = sorted(df['Season'].unique())
    driver_synergy = df[df['Driver'] == selected_driver].set_index('Season').reindex(seasons)['SynergyScore']
    avg_synergy = df.groupby('Season')['SynergyScore'].mean().reindex(seasons)
    best_synergy = df.groupby('Season')['SynergyScore'].max().reindex(seasons)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(seasons, driver_synergy, label=selected_driver, marker='o')
    ax.plot(seasons, avg_synergy, linestyle='dotted', color='gray', label='Average Synergy')
    ax.plot(seasons, best_synergy, linewidth=3, color='green', label='Best Synergy')

    # Labels and title
    ax.set_title(f'Synergy Trends: {selected_driver} vs Average and Best')
    ax.set_xlabel('Season')
    ax.set_ylabel('Synergy Score')
    ax.set_ylim(0, 100)
    ax.legend()

    # Show in Streamlit
    st.pyplot(fig)

drivers_list = get_latest_season_drivers()
data = get_historic_synergies() 
driver = st.sidebar.selectbox('Pick a driver', options=drivers_list)
show_driver_button = st.sidebar.button('Show Driver Synergy')
show_model_stats = st.sidebar.button('SHow model stats')




if show_model_stats:
    st.dataframe(data)
    plot_col1, plot_col2 = st.columns([1,2])
    with plot_col1:
        st.markdown('Distribution of synergy levels over the dataset')
        plot_synergy_level_distribution(data)
    with plot_col2:
        st.markdown('Top ten synergy levels from the dataset')
        plot_top_synergies(data, top=10)

if show_driver_button:
    plot_driver_synergies(driver, data)