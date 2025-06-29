import streamlit as st
import fastf1
from fastf1 import plotting
import pandas as pd
import matplotlib.pyplot as plt

plotting.setup_mpl()

st.title("Telemetry Comparison Between Teammates")

# --- Sidebar selectors ---
st.sidebar.header("Telemetry Comparison Settings")

season = st.sidebar.selectbox("Season", options=list(range(2018, 2024)), index=5)
session_type = st.sidebar.selectbox("Session", options=["Q", "R", "FP1", "FP2", "FP3"], index=0)
gp_name = st.sidebar.text_input("Grand Prix Name (e.g., 'Monza')")
team = st.sidebar.text_input("Team Name (e.g., 'Mercedes')")

load_button = st.sidebar.button("Load and Show Telemetry")

# --- Helper function ---
@st.cache_data(show_spinner="Loading session data, please wait...")
def load_session_data(year, gp_name, session_type):
    event = fastf1.get_event(year, gp_name)
    session = event.get_session(session_type)
    session.load(laps=True, telemetry=True, weather=False, messages=False, livedata=False)
    return session

if load_button and gp_name and team:
    try:
        # Load session
        session = load_session_data(season, gp_name, session_type)

        # Get laps data
        laps = session.laps
        if laps.empty:
            st.error("No lap data found for this session.")
        else:
            # Find team drivers
            team_drivers = laps[laps['Team'] == team]['Driver'].unique()
            if len(team_drivers) < 2:
                st.error(f"Not enough drivers for team '{team}' in this session.")
            else:
                driver1, driver2 = team_drivers[0], team_drivers[1]

                # Get fastest lap for each driver
                lap1 = laps.pick_driver(driver1).pick_fastest()
                lap2 = laps.pick_driver(driver2).pick_fastest()

                if lap1 is None or lap2 is None:
                    st.error("One or both drivers have no valid fastest lap data.")
                else:
                    tel1 = lap1.get_car_data().add_distance()
                    tel2 = lap2.get_car_data().add_distance()

                    # Plot
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(tel1['Distance'], tel1['Speed'], label=f"{driver1} fastest lap")
                    ax.plot(tel2['Distance'], tel2['Speed'], label=f"{driver2} fastest lap")
                    ax.set_xlabel("Distance (m)")
                    ax.set_ylabel("Speed (km/h)")
                    ax.set_title(f"Speed Comparison: {driver1} vs {driver2}")
                    ax.legend()
                    st.pyplot(fig)

                    # Optionally show driver names
                    st.write(f"Drivers compared: **{driver1}** and **{driver2}**")

    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
