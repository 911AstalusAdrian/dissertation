import streamlit as st
import fastf1
import pandas as pd
import matplotlib.pyplot as plt
from fastf1 import plotting

plotting.setup_mpl()

st.title("Teammate Telemetry Comparison (Qualifying)")

# --- Sidebar selectors ---
st.sidebar.header("Telemetry Settings")

seasons = list(range(2018, 2024))
selected_season = st.sidebar.selectbox("Select Season", options=seasons, index=len(seasons)-1)

# --- Get events for selected season ---
@st.cache_data(show_spinner="Loading races...")
def get_race_events(season):
    schedule = fastf1.get_event_schedule(season)
    return schedule[['EventName', 'EventDate']]

events_df = get_race_events(selected_season)
race_names = events_df['EventName'].tolist()

selected_race = st.sidebar.selectbox("Select Race", options=race_names)

# --- Load qualifying session and get teams ---
@st.cache_data(show_spinner="Loading qualifying data...")
def get_teams_for_race(season, race_name):
    try:
        event = fastf1.get_event(season, race_name)
        quali = event.get_session('Q')
        quali.load(laps=True, telemetry=False, weather=False, messages=False, livedata=False)
        teams = quali.laps['Team'].dropna().unique().tolist()
        return teams
    except Exception as e:
        return []

if selected_race:
    available_teams = get_teams_for_race(selected_season, selected_race)
    if available_teams:
        selected_team = st.sidebar.selectbox("Select Team", options=available_teams)
    else:
        selected_team = None
else:
    selected_team = None

# --- Load telemetry and plot ---
if st.sidebar.button("Load and Show Telemetry") and selected_team:
    try:
        event = fastf1.get_event(selected_season, selected_race)
        quali = event.get_session('Q')
        quali.load(laps=True, telemetry=True, weather=False, messages=False, livedata=False)

        laps = quali.laps
        team_laps = laps[laps['Team'] == selected_team]

        drivers = team_laps['Driver'].unique()
        if len(drivers) < 2:
            st.error(f"Team {selected_team} has fewer than 2 drivers in this session.")
        else:
            driver1, driver2 = drivers[0], drivers[1]

            lap1 = team_laps.pick_driver(driver1).pick_fastest()
            lap2 = team_laps.pick_driver(driver2).pick_fastest()

            if lap1 is None or lap2 is None:
                st.error("Could not find fastest laps for both drivers.")
            else:
                tel1 = lap1.get_car_data().add_distance()
                tel2 = lap2.get_car_data().add_distance()

                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(tel1['Distance'], tel1['Speed'], label=f"{driver1} fastest lap")
                ax.plot(tel2['Distance'], tel2['Speed'], label=f"{driver2} fastest lap")
                ax.set_xlabel("Distance (m)")
                ax.set_ylabel("Speed (km/h)")
                ax.set_title(f"Qualifying Speed Comparison: {driver1} vs {driver2}")
                ax.legend()
                st.pyplot(fig)

                st.write(f"Drivers compared: **{driver1}** and **{driver2}**")

    except Exception as e:
        st.error(f"Error: {e}")
