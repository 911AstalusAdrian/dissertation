import streamlit as st
import pandas as pd

from src.data_ingestion.openf1_loader import *


def load_driver_data():
    latest_session = get_last_session()
    return get_driver(driver_number=1, session_key=latest_session)


def load_drivers_data():
    drivers = get_distinct_drivers()
    return drivers

def load_teams_data():
    pass

def load_sessions_data(circuit_key=None, meeting_key=None, session_key=None, session_name=None, session_type=None, year=None):
    sessions = get_sessions(circuit_key, meeting_key, session_key, session_name, session_type, year)
    return sessions.count()

def load_laps_data():
    pass

def get_stats():
    drivers_df = load_drivers_data()[0]
    teams_df = load_teams_data()
    sessions_df = load_sessions_data()
    laps_df = load_laps_data()

    return drivers_df, teams_df, sessions_df, laps_df

st.title('F1 Driver-Car Compatibility Dashboard')
st.markdown("""
This app explores how well drivers 'fit' their cars based on telemetry and performance data.
It combines real-world Formula 1 race data from multiple APIs to analyse pace, style and synergy.
""")


# num_drivers, num_teams, num_sessions, total_laps = get_stats()
# col1, col2, col3, col4 = st.columns(4)
# col1.metric("Drivers", num_drivers)
# col2.metric("Teams", num_teams)
# col3.metric("Sessions", num_sessions)
# col4.metric("Laps", total_laps)


drivers_df = load_drivers_data()
st.dataframe(drivers_df)