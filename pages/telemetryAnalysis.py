import fastf1
from fastf1 import plotting
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

plotting.setup_mpl()

@st.cache_data
def get_event_schedule(season):
    return fastf1.get_event_schedule(season)

@st.cache_data
def load_session(year, gp_name, session_type):
    event = fastf1.get_event(year, gp_name)
    session = event.get_session(session_type)
    session.load()
    return session

def interpolate_telemetry(tel, common_distance):
    tel_interp = tel.set_index('Distance').reindex(common_distance).interpolate(method='index').reset_index()
    tel_interp.rename(columns={'index': 'Distance'}, inplace=True)
    return tel_interp

# --- Streamlit UI ---
st.title("Teammate Telemetry Comparison")

season = st.selectbox("Select Season", list(range(2018, 2025)))
event_schedule = get_event_schedule(season)
races = event_schedule['EventName'].tolist()
race = st.selectbox("Select Race", races)

session_type = st.selectbox("Session Type", ['Qualifying', 'Race'])

if st.button("Load Session and Show Teammates"):
    session = load_session(season, race, session_type)
    drivers = session.results['FullName'].unique().tolist()
    team_options = session.results['TeamName'].unique().tolist()

    team = st.selectbox("Select Team", team_options)

    team_drivers = session.results.loc[session.results['TeamName'] == team, 'FullName'].tolist()

    if len(team_drivers) < 2:
        st.warning("This team has less than two drivers in this session.")
    else:
        driver1 = team_drivers[0]
        driver2 = team_drivers[1]

        # Get laps
        laps_driver1 = session.laps.pick_driver(driver1).pick_fastest()
        laps_driver2 = session.laps.pick_driver(driver2).pick_fastest()

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
