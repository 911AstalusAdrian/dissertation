import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import timedelta
from src.data_ingestion.openf1_loader import *
from src.data_ingestion.fastf1_loader import get_kpis_from_session, get_session_top5_drivers_laps, get_session_tyre_distribution
from src.utils.df_utils import format_laptime

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

def get_session_kpis(season, session_type, selected_round):
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

rounds = None
race_sessions = None
kpis = None

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
    st.markdown('')
    load_data = st.button('Get session info')



### KPI Data
if load_data:
    with st.spinner('Loading session data...'):
        try:
            kpis = get_session_kpis(season, selected_round, session_type)
            top5_driver_laps = get_session_top5_drivers_laps(season, selected_round, session_type)
            compound_summary = get_session_tyre_distribution(season, selected_round, session_type)
            ### KPI Cards
            if kpis:
                    cols = st.columns(6)
                    cols[0].metric("Fastest Driver", kpis["fastest_driver"])
                    cols[1].metric("Fastest Lap Time", format_laptime(kpis["fastest_lap"]))
                    cols[2].metric("Fastest Lap Compound", kpis["fastest_lap_compound"])
                    cols[3].metric("Total Laps", kpis["total_laps"])
                    cols[4].metric("Most Laps by a Driver", f"{kpis['top_driver']} - {kpis['max_laps']}")
                    cols[5].metric('Most Laps by a Team', f'{kpis['top_team']} - {kpis['max_laps_team']}')
            else:
                st.warning("No KPIs were generated from this session.")

            # Top 5 drivers laptimes line chart
            if not top5_driver_laps.empty:
                fig = px.line(
                    top5_driver_laps,
                    x='LapNumber',
                    y='LapTimeSeconds',
                    color = 'Driver',
                    markers = True,
                    title = 'Lap Time trend for top 5 drivers',
                    labels = {
                        'LapNumber': 'Lap Number',
                        'LapTimeSeconds': 'Lap Time (s)',
                        'Driver': 'Driver'
                    }
                )
                fig.update_layout(
                    xaxis=dict(dtick=1),
                    yaxis_title='Lap Time (seconds)',
                    legend_title='Driver',
                    template='plotly_white'
                )
                st.plotly_chart(fig, use_container_width=True)  
            else:
                st.warning('No Top 5 driver laptimes generated from this session')

            # Tyre Compound Usage bar/pie chart
            if not compound_summary.empty:
                fig = px.pie(
                compound_summary,
                names='Compound',
                values='TotalLaps',
                title='Tyre Compound Distribution (Total Laps)',
                color_discrete_map={
                    'HARD': '#FFFFFF',
                    'MEDIUM': '#FFD700',
                    'SOFT': '#FF4C4C'})

                col1, col2 = st.columns([2, 3])  # Adjust width ratios as needed

                # Display pie chart and capture click
                with col1:
                  selected = st.plotly_chart(fig, use_container_width=True)

                # Display metrics based on selected compound
                with col2:
                    st.dataframe(compound_summary)
            else:
                st.warning('No compound summary was generated from this session')
        except Exception as e:
            st.error(f"An error occurred: {e}")