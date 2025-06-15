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


data = get_historic_synergies()
synergy_counts = data['SynergyLevel'].value_counts().sort_index()

st.dataframe(data)

synergy_df = synergy_counts.reset_index()
synergy_df.columns = ['SynergyLevel', 'Count']
synergy_df = synergy_df.set_index('SynergyLevel')
st.bar_chart(synergy_df)

# Score Range	Class Label
# 85 – 100	⭐ Excellent
# 70 – 84	👍 Good
# 50 – 69	⚖️ Moderate
# 30 – 49	⚠️ Poor
# 1 – 29	❌ Very Poor