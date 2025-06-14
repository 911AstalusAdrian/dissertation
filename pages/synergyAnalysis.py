import streamlit as st
import pandas as pd

from src.data_ingestion.openf1_loader import get_recent_drivers
from src.data_ingestion.fastf1_loader import get_synergy_metrics
from src.utils.plot_utils import RACE_COLOR, QUALI_COLOR

@st.cache_data(show_spinner='Loading list of recent drivers...')
def get_latest_drivers():
    recent_drivers_list = get_recent_drivers()
    return list(recent_drivers_list)

@st.cache_data(show_spinner='Getting synergy stats...')
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

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Avg Qualifying Pos", f"{synergy_stats['Avg_Q']:.2f}")
    col2.metric("Avg Finish Pos", f"{synergy_stats['Avg_R']:.2f}")
    col3.metric("DNF Rate", f"{synergy_stats['DNFRate']:.1f}%")
    col4.metric("Lap Consistency (Std Dev)", f"{synergy_stats['Lap_stdev']:.2f}s")
    col5.metric("Avg Delta to Teammate", f"{synergy_stats['Teammate_delta']:+.2f}s")

    st.divider()

    qualis = synergy_stats.get('Q_positions')
    races = synergy_stats.get('R_positions')
    lap_deltas = synergy_stats.get('RaceLapDeltas')

    plot_col1, plot_col2 = st.columns(2)
    with plot_col1:
        plot1_data = {
            'Qualis': qualis,
            'Races': races
        }

        df = pd.DataFrame(plot1_data)
        df.index.name = 'Round'
        st.line_chart(df, color=[QUALI_COLOR, RACE_COLOR])
    with plot_col2:
        plot2_data = {
            'LapDelta': lap_deltas
        }
        df = pd.DataFrame(plot2_data)
        st.line_chart(df, color=f'#{synergy_stats.get('Color')}')