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
        quali = fastf1.get_session(season, selected_round, 'Q')
        quali.load()

        # Get drivers from the selected team
        team_drivers_df = quali.results[quali.results['TeamName'] == team]
        drivers = team_drivers_df['Abbreviation'].values

        if len(drivers) != 2:
            st.error(f"Expected 2 drivers for {team}, but found {len(drivers)}.")
        else:
            driver1, driver2 = drivers

            laps1 = quali.laps.pick_driver(driver1).pick_quicklaps()
            laps2 = quali.laps.pick_driver(driver2).pick_quicklaps()

            if laps1.empty or laps2.empty:
                st.error("One or both drivers have no valid quicklaps.")
            else:
                fastest_lap1 = laps1.pick_fastest()
                fastest_lap2 = laps2.pick_fastest()

                tel1 = fastest_lap1.get_car_data().add_distance()
                tel2 = fastest_lap2.get_car_data().add_distance()

                df1 = pd.DataFrame({
                    "Distance": tel1["Distance"],
                    "Speed": tel1["Speed"],
                    "Throttle": tel1["Throttle"],
                    "Brake": tel1["Brake"]
                })

                df2 = pd.DataFrame({
                    "Distance": tel2["Distance"],
                    "Speed": tel2["Speed"],
                    "Throttle": tel2["Throttle"],
                    "Brake": tel2["Brake"]
                })

                # Merge
                merged = pd.merge_asof(
                    df1.sort_values("Distance"),
                    df2.sort_values("Distance"),
                    on="Distance",
                    direction="nearest",
                    suffixes=(f"_{driver1}", f"_{driver2}"),
                    tolerance=1
                ).dropna()

                # Create Plotly figure
                fig = go.Figure()

                # Speed
                fig.add_trace(go.Scatter(
                    x=merged["Distance"],
                    y=merged[f"Speed_{driver1}"],
                    name=f"{driver1} Speed",
                    line=dict(color='red')
                ))

                fig.add_trace(go.Scatter(
                    x=merged["Distance"],
                    y=merged[f"Speed_{driver2}"],
                    name=f"{driver2} Speed",
                    line=dict(color='blue')
                ))

                # Throttle
                fig.add_trace(go.Scatter(
                    x=merged["Distance"],
                    y=merged[f"Throttle_{driver1}"],
                    name=f"{driver1} Throttle",
                    line=dict(color='red', dash='dot')
                ))

                fig.add_trace(go.Scatter(
                    x=merged["Distance"],
                    y=merged[f"Throttle_{driver2}"],
                    name=f"{driver2} Throttle",
                    line=dict(color='blue', dash='dot')
                ))

                # Brake
                fig.add_trace(go.Scatter(
                    x=merged["Distance"],
                    y=merged[f"Brake_{driver1}"],
                    name=f"{driver1} Brake",
                    line=dict(color='red', dash='dash')
                ))

                fig.add_trace(go.Scatter(
                    x=merged["Distance"],
                    y=merged[f"Brake_{driver2}"],
                    name=f"{driver2} Brake",
                    line=dict(color='blue', dash='dash')
                ))

                fig.update_layout(
                    title=f"Qualifying Telemetry Comparison - {team} ({season}, Round {selected_round})",
                    xaxis_title='Distance (m)',
                    yaxis_title='Metric Value',
                    hovermode="x unified",
                    template="plotly_dark",
                    height=700
                )

                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Failed to load or plot telemetry: {e}")