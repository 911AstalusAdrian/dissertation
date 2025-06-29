import streamlit as st
import fastf1
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit section
st.title("Telemetry Comparison Between Teammates")

# User inputs
season = st.selectbox("Season", options=list(range(2018, 2024)))
race = st.text_input("Grand Prix Name (e.g., 'Monza')")
session_type = st.selectbox("Session", options=["Q", "R", "FP1", "FP2", "FP3"])
team = st.text_input("Team name (exactly as in data, e.g., 'Mercedes')")
load_button = st.button("Load Session")

# Helper function to load session with correct flags
@st.cache_data(show_spinner="Loading session data...")
def load_session(year, gp_name, session_type):
    event = fastf1.get_event(year, gp_name)
    session = event.get_session(session_type)
    session.load(laps=True, telemetry=True, weather=False, messages=False, livedata=False)
    return session

if load_button and race and team:
    try:
        session = load_session(season, race, session_type)

        # Check if laps are loaded
        if session.laps.empty:
            st.error("No lap data available for this session.")
        else:
            # Find drivers from the specified team
            laps = session.laps
            team_drivers = laps[laps['Team'] == team]['Driver'].unique()

            if len(team_drivers) < 2:
                st.error(f"Not enough drivers found for team {team} in this session.")
            else:
                driver1, driver2 = team_drivers[0], team_drivers[1]

                # Get fastest lap for each driver
                lap1 = laps.pick_driver(driver1).pick_fastest()
                lap2 = laps.pick_driver(driver2).pick_fastest()

                if lap1 is None or lap2 is None:
                    st.error("One or both drivers do not have valid lap data.")
                else:
                    tel1 = lap1.get_car_data().add_distance()
                    tel2 = lap2.get_car_data().add_distance()

                    # Plot speed telemetry
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(tel1['Distance'], tel1['Speed'], label=f"{driver1} Fastest Lap")
                    ax.plot(tel2['Distance'], tel2['Speed'], label=f"{driver2} Fastest Lap")
                    ax.set_xlabel("Distance (m)")
                    ax.set_ylabel("Speed (km/h)")
                    ax.legend()
                    ax.set_title(f"Speed Comparison: {driver1} vs {driver2}")
                    st.pyplot(fig)

    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
