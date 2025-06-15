import streamlit as st
import pandas as pd
import numpy as np

# from src.data_ingestion.openf1_loader import get_recent_drivers
# from src.data_ingestion.fastf1_loader import get_synergy_metrics
# from src.utils.plot_utils import RACE_COLOR, QUALI_COLOR

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

    print(top_synergies)
    st.bar_chart(top_synergies[['SynergyScore']], horizontal=True)

data = get_historic_synergies()
st.dataframe(data)

plot_col1, plot_col2 = st.columns([1,2])
with plot_col1:
    st.markdown('Distribution of synergy levels over the dataset')
    plot_synergy_level_distribution(data)
with plot_col2:
    st.markdown('Top ten synergy levels from the dataset')
    plot_top_synergies(data, top=10)