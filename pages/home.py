import streamlit as st
import pandas as pd

from src.data_ingestion.openf1_loader import *


### Driver-related methods
def load_driver_data():
    latest_session = get_last_session()
    return get_driver(driver_number=1, session_key=latest_session)

def load_drivers_data():
    drivers = get_distinct_drivers()
    return drivers

### Session-related methods
def load_sessions_data(circuit_key=None, meeting_key=None, session_key=None, session_name=None, session_type=None, year=None):
    sessions = get_sessions(circuit_key, meeting_key, session_key, session_name, session_type, year)
    return sessions

### Lap-related methods
def load_laps_data():
    pass

def load_laps_count():
    return get_laps_count()

def get_stats():
    drivers_df = get_distinct_drivers_count()
    sessions_df = get_sessions_count()
    laps_df = get_laps_count()

    return drivers_df, sessions_df, laps_df, 200




st.title('F1 Driver-Car Compatibility Dashboard')
st.markdown("""
This app explores how well drivers 'fit' their cars based on telemetry and performance data.
It combines real-world Formula 1 race data from multiple APIs to analyse pace, style and synergy.
""")


total_drivers, total_teams, total_laps , last_value = get_stats()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Drivers", total_drivers)
col2.metric("Teams", total_teams)
col3.metric("Laps", total_laps)
col4.metric("Last KPI", last_value)


drivers_df = load_drivers_data()
st.dataframe(drivers_df)