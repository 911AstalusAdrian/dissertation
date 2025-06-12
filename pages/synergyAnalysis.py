import streamlit as st
import pandas as pd

from src.data_ingestion.openf1_loader import get_fulltime_drivers, get_teams_for_driver
from src.data_ingestion.fastf1_loader import get_event_names_for_season, get_events_for_season

def get_list_of_drivers():
    distinct_drivers_df = get_fulltime_drivers()

    return distinct_drivers_df['full_name'].to_list()

def get_driver_teams(driver_name):
    return get_teams_for_driver(driver_name)

st.sidebar.header("Select Inputs")
driver = st.sidebar.selectbox("Driver", get_list_of_drivers())
season = st.sidebar.selectbox("Season", [2023, 2024, 2025])
races = st.sidebar.selection('Race', get_event_names_for_season(season))

if st.sidebar.button("Analyze Synergy"):

    all_races = get_event_names_for_season(season)

    # Placeholder: compute synergy_stats, lap_time_df, position_deltas
    synergy_stats = {
        "avg_quali_pos": 3.2,
        "avg_finish_pos": 2.8,
        "dnf_rate": 0.1,
        "lap_std": 0.45,
        "delta_to_teammate": -1.2
    }

    # st.subheader(f"Synergy Report for {driver} ({season})")

    # KPI cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Qualifying Pos", f"{synergy_stats['avg_quali_pos']:.2f}")
    col2.metric("Avg Finish Pos", f"{synergy_stats['avg_finish_pos']:.2f}")
    col3.metric("DNF Rate", f"{synergy_stats['dnf_rate']*100:.1f}%")

    col4, col5 = st.columns(2)
    col4.metric("Lap Consistency (Std Dev)", f"{synergy_stats['lap_std']:.2f}s")
    col5.metric("Avg Delta to Teammate", f"{synergy_stats['delta_to_teammate']:+.2f} pos")

    st.divider()

    # Trend Charts (placeholders)
    st.subheader("Qualifying vs Race Position")
    st.line_chart(pd.DataFrame({
        "Qualifying": [4, 3, 2, 5],
        "Race": [2, 1, 2, 3]
    }, index=["Bahrain", "Saudi Arabia", "Australia", "Azerbaijan"]))

    st.subheader("Lap Time Consistency")
    # st.box_chart(pd.DataFrame({
    #     "GP": ["Bahrain", "Saudi", "Australia", "Azerbaijan"],
    #     "LapTime": [0.3, 0.25, 0.45, 0.4]
    # }))

    st.subheader("Delta to Teammate per Race")
    st.bar_chart(pd.Series([-0.5, -1.0, -1.2, 0.0], index=["Bahrain", "Saudi", "Australia", "Azerbaijan"]))

# picker_col1, picker_col2 = st.columns(2)
# with picker_col1:
#     driver = st.selectbox('Select Driver', options=get_list_of_drivers())
# with picker_col2:
#     if driver:
#         st.selectbox('Select Team', options=get_driver_teams(driver))