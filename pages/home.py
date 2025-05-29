import streamlit as st
import pandas as pd

from src.data_ingestion.openf1_loader import *
from src.data_ingestion.fastf1_loader import get_kpis_from_session


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
    # laps_df = get_laps_count()
    laps_df = 155489

    return drivers_df, sessions_df, laps_df, 200

def get_session_data(season, session_type, selected_round):
    return get_kpis_from_session(season, session_type, selected_round)

### Title and markdown
st.title('F1 Driver-Car Compatibility Dashboard')
st.markdown("""
This app explores how well drivers 'fit' their cars based on telemetry and performance data.
It combines real-world Formula 1 race data from multiple APIs to analyse pace, style and synergy.
""")

### Session picker
if "season" not in st.session_state:
    st.session_state.season = 2023

if "sessions" not in st.session_state:
    st.session_state.sessions = {}

sessions = {}
rounds = []
race_sessions = []

picker_col1, picker_col2, picker_col3, picker_col4 = st.columns([2,2,2,1])
with picker_col1:
    season = st.selectbox('Choose Season', options=[2023, 2024, 2025])
    st.session_state.season = season
    st.session_state.sessions = get_races_per_season(season=season)
    rounds = list(st.session_state.sessions.keys())
with picker_col2:
    if st.session_state.season:
        selected_round = st.selectbox('Round', options=rounds)
with picker_col3:
    if selected_round:
        race_sessions = st.session_state.sessions[selected_round]
        session_type = st.selectbox('Session Type', race_sessions)
with picker_col4:
    if st.button('Get session info'):
        kpis = get_session_data(season=st.session_state.season, session_type=session_type, selected_round=selected_round)

### KPI Data
cols = st.columns(4)
cols[0].metric("Fastest Driver", kpis["fastest_driver"])
cols[1].metric("Fastest Lap Time", str(kpis["fastest_lap"]))
cols[2].metric("Fastest Lap Compound", kpis["fastest_compound"])
cols[3].metric("Total Laps", kpis["total_laps"])
 ## Fastest Lap? Most Laps? Change based on the session 
## 4th metric: Fastest Lap? Most Laps of a driver of the session?
## maybe add a 5th metric based on the session?

# drivers_df = load_drivers_data()
# st.dataframe(drivers_df)