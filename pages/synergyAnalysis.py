import streamlit as st
import pandas as pd

from src.data_ingestion.openf1_loader import get_recent_drivers
from src.data_ingestion.fastf1_loader import get_synergy_metrics

@st.cache_data(show_spinner='Loading list of recent drivers...')
def get_latest_drivers():
    recent_drivers_list = get_recent_drivers()
    return list(recent_drivers_list)

def get_synergy_stats(driver, season):
    synergy_results = get_synergy_metrics(driver, season)
    return synergy_results

cols = st.columns(3)
with cols[0]:
    driver = st.selectbox("Driver", get_latest_drivers())
with cols[1]:
    season = st.selectbox("Season", [2023, 2024, 2025])
with cols[2]:
    st.markdown('')
    analyse_synergy = st.button("Analyze Synergy")

if analyse_synergy:

    synergy_stats = get_synergy_stats(driver, season)
    st.markdown(f'Analysing {driver} fror the {season} season')

    # average quali position
    # average finish position
    # dnf rate
    # lap standard deviation
    # delta to teammate

    # KPI cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Qualifying Pos", f"{synergy_stats['Avg_Q']:.2f}")
    col2.metric("Avg Finish Pos", f"{synergy_stats['Avg_R']:.2f}")
    col3.metric("DNF Rate", f"{synergy_stats['DNFRate']:.1f}%")

    # col4, col5 = st.columns(2)
    # col4.metric("Lap Consistency (Std Dev)", f"{synergy_stats['lap_std']:.2f}s")
    # col5.metric("Avg Delta to Teammate", f"{synergy_stats['delta_to_teammate']:+.2f} pos")

    st.divider()

    qualis = synergy_stats.get('Q_positions')
    races = synergy_stats.get('R_positions')
    data = {
        'Qualis': qualis,
        'Races': races
    }

    df = pd.DataFrame(data)
    df.index.name = 'Round'
    st.line_chart(df)

    # # Trend Charts (placeholders)
    # st.subheader("Qualifying vs Race Position")
    # st.line_chart(pd.DataFrame({
    #     "Qualifying": [4, 3, 2, 5],
    #     "Race": [2, 1, 2, 3]
    # }, index=["Bahrain", "Saudi Arabia", "Australia", "Azerbaijan"]))

    # st.subheader("Lap Time Consistency")
    # st.box_chart(pd.DataFrame({
    #     "GP": ["Bahrain", "Saudi", "Australia", "Azerbaijan"],
    #     "LapTime": [0.3, 0.25, 0.45, 0.4]
    # }))

    # st.subheader("Delta to Teammate per Race")
    # st.bar_chart(pd.Series([-0.5, -1.0, -1.2, 0.0], index=["Bahrain", "Saudi", "Australia", "Azerbaijan"]))

# picker_col1, picker_col2 = st.columns(2)
# with picker_col1:
#     driver = st.selectbox('Select Driver', options=get_list_of_drivers())
# with picker_col2:
#     if driver:
#         st.selectbox('Select Team', options=get_driver_teams(driver))