import streamlit as st
import fastf1
import plotly.graph_objects as go
import pandas as pd 

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

                df1 = pd.DataFrame({
                    "Distance": tel_driver1["Distance"],
                    "Speed": tel_driver1["Speed"]
                })
                df2 = pd.DataFrame({
                    "Distance": tel_driver2["Distance"],
                    "Speed": tel_driver2["Speed"]
                })

                # Merge by nearest Distance
                merged = pd.merge_asof(
                    df1.sort_values("Distance"),
                    df2.sort_values("Distance"),
                    on="Distance",
                    direction="nearest",
                    suffixes=(f"_{driver1}", f"_{driver2}"),
                    tolerance=1
                )

                merged = merged.dropna()

                # Create plotly figure
                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=merged["Distance"],
                    y=merged[f"Speed_{driver1}"],
                    mode='lines',
                    name=f"{driver1} Speed",
                    line=dict(color='red')
                ))

                fig.add_trace(go.Scatter(
                    x=merged["Distance"],
                    y=merged[f"Speed_{driver2}"],
                    mode='lines',
                    name=f"{driver2} Speed",
                    line=dict(color='blue')
                ))

                fig.update_layout(
                    title=f"Qualifying Fastest Lap Telemetry - {team} ({season}, Round {selected_round})",
                    xaxis_title='Distance (m)',
                    yaxis_title='Speed (km/h)',
                    legend_title='Driver',
                    hovermode="x unified",
                    template="plotly_dark"
                )

                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Failed to load session: {e}")