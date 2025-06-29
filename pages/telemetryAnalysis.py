import streamlit as st
import fastf1
import matplotlib.pyplot as plt
from src.data_ingestion.openf1_loader import *

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

            laps_driver1 = quali_session.laps.pick_driver(driver1).pick_quicklaps()
            laps_driver2 = quali_session.laps.pick_driver(driver2).pick_quicklaps()

            if laps_driver1.empty or laps_driver2.empty:
                st.error("One or both drivers have no valid quicklaps.")
            else:
                fastest_lap_driver1 = laps_driver1.pick_fastest()
                fastest_lap_driver2 = laps_driver2.pick_fastest()

                tel_driver1 = fastest_lap_driver1.get_car_data().add_distance()
                tel_driver2 = fastest_lap_driver2.get_car_data().add_distance()

                # Create Pandas DataFrames for each driver
                df1 = pd.DataFrame({
                    "Distance": tel_driver1["Distance"],
                    f"Speed ({driver1})": tel_driver1["Speed"]
                })
                df2 = pd.DataFrame({
                    "Distance": tel_driver2["Distance"],
                    f"Speed ({driver2})": tel_driver2["Speed"]
                })

                # Merge on Distance (we do an outer join and interpolate to align them)
                merged = pd.merge_asof(
                    df1.sort_values("Distance"),
                    df2.sort_values("Distance"),
                    on="Distance",
                    direction="nearest",
                    tolerance=1  # small tolerance to avoid misalignments
                )

                merged = merged.dropna()

                # Set Distance as index for st.line_chart
                merged = merged.set_index("Distance")

                # Show using Streamlit line_chart
                st.line_chart(merged)

    except Exception as e:
        st.error(f"Failed to load session: {e}")
