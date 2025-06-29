import streamlit as st
import fastf1
import fastf1.plotting
import pandas as pd
import plotly.express as px

# fastf1.Cache.enable_cache('./cache')  # Important if not done yet

@st.cache_data(show_spinner="Loading session data...")
def load_session(season, race_name, session_type):
    session = fastf1.get_session(season, race_name, session_type)
    session.load()
    return session

st.header("Teammate Telemetry & Delta Comparison")

# --- Sidebar selections ---
season = st.sidebar.selectbox("Select Season", list(range(2018, 2025)))
session_type = 'Q'

schedule = fastf1.get_event_schedule(season)
race_name = st.sidebar.selectbox("Select Race", schedule['EventName'].tolist())

if st.sidebar.button("Compare Teammates"):
    session = load_session(season, race_name, session_type)
    race_results = session.results

    teams = race_results['TeamName'].unique()
    team_name = st.selectbox("Select Team", teams)

    team_drivers = race_results.loc[race_results['TeamName'] == team_name]['Abbreviation'].values

    if len(team_drivers) < 2:
        st.warning("This team had fewer than 2 drivers in this session.")
    else:
        # Get fastest laps
        laps_driver1 = session.laps.pick_driver(team_drivers[0]).pick_fastest()
        laps_driver2 = session.laps.pick_driver(team_drivers[1]).pick_fastest()

        tel1 = laps_driver1.get_car_data().add_distance()
        tel2 = laps_driver2.get_car_data().add_distance()

        # --- Speed plot ---
        fig = px.line(x=tel1['Distance'], y=tel1['Speed'], labels={'x': 'Distance (m)', 'y': 'Speed (km/h)'},
                      title=f"Speed Comparison: {team_drivers[0]} vs {team_drivers[1]}")
        fig.add_scatter(x=tel2['Distance'], y=tel2['Speed'], name=team_drivers[1])
        fig.update_traces(name=team_drivers[0], selector=dict(type='scatter', mode='lines'))
        st.plotly_chart(fig)

        # --- Delta plot ---
        delta_time = fastf1.utils.delta_time(laps_driver1, laps_driver2)
        fig_delta = px.line(x=tel1['Distance'], y=delta_time,
                            labels={'x': 'Distance (m)', 'y': 'Delta Time (s)'},
                            title=f"Delta Time Along Lap: {team_drivers[0]} vs {team_drivers[1]}")
        st.plotly_chart(fig_delta)

        # --- Optional: Throttle ---
        if st.checkbox("Show throttle comparison"):
            fig_throttle = px.line(x=tel1['Distance'], y=tel1['Throttle'], labels={'x': 'Distance (m)', 'y': 'Throttle (%)'},
                                   title="Throttle Comparison")
            fig_throttle.add_scatter(x=tel2['Distance'], y=tel2['Throttle'], name=team_drivers[1])
            fig_throttle.update_traces(name=team_drivers[0], selector=dict(type='scatter', mode='lines'))
            st.plotly_chart(fig_throttle)

        # --- Optional: Brake ---
        if st.checkbox("Show brake comparison"):
            fig_brake = px.line(x=tel1['Distance'], y=tel1['Brake'], labels={'x': 'Distance (m)', 'y': 'Brake (%)'},
                                title="Brake Comparison")
            fig_brake.add_scatter(x=tel2['Distance'], y=tel2['Brake'], name=team_drivers[1])
            fig_brake.update_traces(name=team_drivers[0], selector=dict(type='scatter', mode='lines'))
            st.plotly_chart(fig_brake)

        # --- Sector summary ---
        sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']

        try:
            sector_times1 = [laps_driver1[sec].total_seconds() for sec in sectors]
            sector_times2 = [laps_driver2[sec].total_seconds() for sec in sectors]

            df_sector = pd.DataFrame({
                'Sector': ['Sector 1', 'Sector 2', 'Sector 3'],
                team_drivers[0]: sector_times1,
                team_drivers[1]: sector_times2,
                'Delta (s)': [s1 - s2 for s1, s2 in zip(sector_times1, sector_times2)]
            })
            st.subheader("Sector Time Summary")
            st.dataframe(df_sector.style.format({
                team_drivers[0]: "{:.3f}",
                team_drivers[1]: "{:.3f}",
                'Delta (s)': "{:+.3f}"
            }))
        except Exception as e:
            st.warning(f"Could not extract sector data: {e}")