import streamlit as st
import pandas as pd
import numpy as np

from src.data_ingestion.openf1_loader import get_recent_drivers
from src.data_ingestion.fastf1_loader import get_synergy_metrics
from src.utils.plot_utils import RACE_COLOR, QUALI_COLOR

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

def plot_top_synergies(synergy_df, top=10):
    top_synergies = synergy_df.nlargest(top, 'SynergyScore')
    top_synergies = top_synergies.sort_values('SynergyScore')
    top_synergies['Label'] = f'{top_synergies['Driver']} ({top_synergies['Season']})'

    # top_synergies.drop(columns=['Driver', 'Season'])
    # top_synergies.set_index('SynergyScore')
    # st.bar_chart(top_synergies, horizontal=True)
    st.dataframe(top_synergies)


data = get_historic_synergies()
st.dataframe(data)
plot_synergy_level_distribution(data)
plot_top_synergies(data, top=10)