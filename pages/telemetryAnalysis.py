import streamlit as st
import fastf1
import numpy as np
import plotly.express as px
from src.data_ingestion.openf1_loader import *

def interpolate_telemetry(tel, common_distance):
    tel_interp = tel.set_index('Distance').reindex(common_distance).interpolate(method='index').reset_index()
    tel_interp.rename(columns={'index': 'Distance'}, inplace=True)
    return tel_interp

if "season" not in st.session_state:
    st.session_state.season = 2023

if "sessions" not in st.session_state:
    st.session_state.sessions = {}

if "teams" not in st.session_state:
    st.session_state.teams = []


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
        teams = st.session_state.teams
        team = st.selectbox('Session Team', teams)
with picker_col4:
    st.markdown('')
    load_data = st.button('Compare telemetry')    


if load_data:
    try:
        quali_session = fastf1.get_session(season, selected_round, 'Q')
        quali_session.load()

        # Get drivers for selected team
        team_drivers_df = quali_session.results[quali_session.results['TeamName'] == team]
        drivers = team_drivers_df['Abbreviation'].values


        if len(drivers) < 2:
            st.warning("This team has less than two drivers in this session.")
        else:
            driver1 = drivers[0]
            driver2 = drivers[1]

            # Get laps
            laps_driver1 = quali_session.laps.pick_driver(driver1).pick_fastest()
            laps_driver2 = quali_session.laps.pick_driver(driver2).pick_fastest()

            tel1 = laps_driver1.get_telemetry().add_distance()
            tel2 = laps_driver2.get_telemetry().add_distance()

            # Common distance range
            min_distance = max(tel1['Distance'].min(), tel2['Distance'].min())
            max_distance = min(tel1['Distance'].max(), tel2['Distance'].max())
            common_distance = np.linspace(min_distance, max_distance, num=500)

            # Interpolate
            tel1_interp = interpolate_telemetry(tel1, common_distance)
            tel2_interp = interpolate_telemetry(tel2, common_distance)

            # Plot Speed
            fig_speed = px.line(x=tel1_interp['Distance'], y=tel1_interp['Speed'],
                                labels={'x': 'Distance (m)', 'y': 'Speed (km/h)'},
                                title=f"Speed Comparison: {driver1} vs {driver2}")
            fig_speed.add_scatter(x=tel2_interp['Distance'], y=tel2_interp['Speed'], name=driver2)
            st.plotly_chart(fig_speed)

            # Plot Throttle
            fig_throttle = px.line(x=tel1_interp['Distance'], y=tel1_interp['Throttle'],
                                labels={'x': 'Distance (m)', 'y': 'Throttle (%)'},
                                title="Throttle Comparison")
            fig_throttle.add_scatter(x=tel2_interp['Distance'], y=tel2_interp['Throttle'], name=driver2)
            st.plotly_chart(fig_throttle)

            # Plot Brake
            fig_brake = px.line(x=tel1_interp['Distance'], y=tel1_interp['Brake'],
                                labels={'x': 'Distance (m)', 'y': 'Brake (%)'},
                                title="Brake Comparison")
            fig_brake.add_scatter(x=tel2_interp['Distance'], y=tel2_interp['Brake'], name=driver2)
            st.plotly_chart(fig_brake)

            # Optional: plot Gear, RPM, Delta, etc.

            st.success("Telemetry comparison plots generated successfully! 🚀")

    except Exception as e:
        st.error(f"Failed to load session: {e}")
