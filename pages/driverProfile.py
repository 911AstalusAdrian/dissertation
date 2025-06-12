import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import timedelta
from src.data_ingestion.openf1_loader import *
from src.data_ingestion.fastf1_loader import get_distinct_drivers
from src.utils.df_utils import format_laptime

@st.cache_data
def get_drivers_data():
    drivers_list = get_distinct_drivers()
    return drivers_list

def get_drivers_list(driver_data: pd.DataFrame):
    return driver_data['DisplayName'].tolist()


drivers_data = get_drivers_data()
# drivers_list = get_drivers_list(drivers_data)

seasons = list(range(2018, 2026))
# --- Layout ---
st.title("Driver Profile")

# --- Sidebar Filters ---
st.sidebar.header("Driver Selector")
driver = st.sidebar.selectbox("Choose Driver", options=drivers_data)  # Example list


## not in the sidebar, make them choices similar to the homepage
# season = st.sidebar.selectbox("Season", options=seasons)
# session_type = st.sidebar.selectbox("Session Type", options=["RACE", "QUALIFYING"])
# round_number = st.sidebar.number_input("Round (optional)", min_value=1, max_value=25, step=1)