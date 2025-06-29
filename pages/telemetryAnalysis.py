import streamlit as st

from src.data_ingestion.openf1_loader import *

if "season" not in st.session_state:
    st.session_state.season = 2023

if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "teams" not in st.session_state:
    st.session_state.teams = {}


rounds = None
race_sessions = None


picker_col1, picker_col2, picker_col3, picker_col4 = st.columns([2,2,2,1])

with picker_col1:
    season = st.selectbox('Choose Season', options=[2023,2024,2025])
    st.session_state.season = season
    st.session_state.sessions = get_races_per_season(season=season)
    st.session_state.teams = get_teams_for_season(season=season)
    rounds = list(st.session_state.sessions.keys())
with picker_col2:
    if st.session_state.season:
        selected_round = st.selectbox('Round', options=rounds)
with picker_col3:
    if selected_round:
        teams = st.session_state.teams[selected_round]
        team = st.selectbox('Session Team', teams)
with picker_col4:
    st.markdown('')
    load_data = st.button('Get session info')    