import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from datetime import timedelta
from src.data_ingestion.openf1_loader import get_driver_image
from src.data_ingestion.fastf1_loader import get_distinct_drivers, get_driver_stats_multiseason, get_race_results_over_seasons
from src.utils.df_utils import format_laptime
from src.utils.plot_utils import TEAM_COLORS

@st.cache_data
def get_drivers_data():
    drivers_list = get_distinct_drivers()
    return drivers_list

@st.cache_data
def get_driver_stats(driver_name):
    stats = get_driver_stats_multiseason(driver_full_name=driver_name)
    return stats

@st.cache_data
def get_driver_results(driver_name):
    results = get_race_results_over_seasons(driver_name)
    return results


@st.cache_data
def get_driver_photo(driver_name):
    return get_driver_image(driver_name)

def plot_driver_results(driver_name):
    df = get_driver_results(driver_name)

    df['RaceIndex'] = range(len(df)) # add a race index

    # Calculate the inverse position so the higher places are at the top of the plot
    df['InvPos'] = df['Position'].astype(int)
    max_pos = df['InvPos'].max()
    df['InvPos'] = max_pos - df['InvPos'] + 1

    fig, ax = plt.subplots(figsize=(12,6))

    segment_x, segment_y = [], []
    prev_team = df.loc[0, 'TeamName']

    for i, row in df.iterrows():
        current_team = row['TeamName']
        color = TEAM_COLORS.get(current_team, '#888888')

        if current_team != prev_team:
            ax.plot(segment_x, segment_y, color = TEAM_COLORS.get(prev_team, '#888888'),
                    linewidth=2, label=prev_team if prev_team not in ax.get_legend_handles_labels()[1] else "")
            segment_x, segment_y = [], []
            prev_team = current_team
        
        segment_x.append(row['RaceIndex'])
        segment_y.append(row['Position'])

    if segment_x:
        ax.plot(segment_x, segment_y, color = TEAM_COLORS.get(prev_team, '#888888'),
                linewidth=2, label=prev_team if prev_team not in ax.get_legend_handles_labels()[1] else "")
        
    ax.set_xlabel('Race Index')
    ax.set_ylabel('Finishing Position')
    ax.set_title('Driver Race Results')
    ax.set_xticks(range(1, len(df)))
    ax.set_yticks(range(max_pos, 1, -1))
    ax.set_yticklabels(list(range(max_pos, 1, -1)))
    ax.invert_yaxis()  # P1 on top
    ax.legend(title="Teams", loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    st.pyplot(fig)


drivers_list = get_drivers_data()
seasons = list(range(2018, 2026))


# --- Sidebar Filters ---
st.sidebar.header("Driver Selector")
driver = st.sidebar.selectbox("Choose Driver", options=drivers_list)  # Example list
show_driver_button = st.sidebar.button('Show Driver Details')

if show_driver_button:
    st.header(f"Stats for {driver}")
    # driver_stats = get_driver_stats(driver)

    # profile_col1, profile_col2 = st.columns([1,3])

    # with profile_col1:
    #     st.image(get_driver_photo(driver), width=150)

    # with profile_col2:
    #     st.markdown(f'Stats for {driver}')
    #     kpi_cols = st.columns(3)
    #     kpi_cols[0].metric('Total Races', driver_stats['Races'])
    #     kpi_cols[1].metric('Finished', driver_stats['Finished'])
    #     kpi_cols[2].metric('DNFs', driver_stats['DNFs'])

    #     kpi_cols2 = st.columns(3)
    #     kpi_cols2[0].metric('Wins', driver_stats['Wins'])
    #     kpi_cols2[1].metric('Podiums', driver_stats['Podiums'])
    #     kpi_cols2[2].metric('Total Points', driver_stats['Points'])

    #     st.markdown(f'Teams raced for: {driver_stats['Teams']}')

    plot_driver_results(driver)
    st.dataframe(get_driver_results(driver))