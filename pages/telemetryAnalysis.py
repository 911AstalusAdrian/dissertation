import streamlit as st
import fastf1
import matplotlib.pyplot as plt

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

        if len(drivers) != 2:
            st.error(f"Expected 2 drivers for {team}, but found {len(drivers)}. Check if both participated in quali.")
        else:
            driver1, driver2 = drivers

            # Pick laps
            laps_driver1 = quali_session.laps.pick_driver(driver1).pick_quicklaps()
            laps_driver2 = quali_session.laps.pick_driver(driver2).pick_quicklaps()

            if laps_driver1.empty or laps_driver2.empty:
                st.error(f"One or both drivers have no valid quicklaps in quali.")
            else:
                fastest_lap_driver1 = laps_driver1.pick_fastest()
                fastest_lap_driver2 = laps_driver2.pick_fastest()

                tel_driver1 = fastest_lap_driver1.get_car_data().add_distance()
                tel_driver2 = fastest_lap_driver2.get_car_data().add_distance()

                # --- Plot example: Speed vs Distance ---
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(tel_driver1['Distance'], tel_driver1['Speed'], label=driver1)
                ax.plot(tel_driver2['Distance'], tel_driver2['Speed'], label=driver2)

                ax.set_xlabel("Distance (m)")
                ax.set_ylabel("Speed (km/h)")
                ax.legend()
                ax.grid(True)

                st.pyplot(fig)


            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(tel_driver1['Distance'], tel_driver1['Throttle'], label=driver1)
            ax.plot(tel_driver2['Distance'], tel_driver2['Throttle'], label=driver2)
            ax.set_xlabel("Distance (m)")
            ax.set_ylabel("Throttle (%)")
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Failed to load session: {e}")