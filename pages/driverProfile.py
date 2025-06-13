import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import timedelta
from src.data_ingestion.openf1_loader import get_driver_image
from src.data_ingestion.fastf1_loader import get_distinct_drivers, get_driver_stats_multiseason, get_race_results_over_seasons
from src.utils.df_utils import format_laptime

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

drivers_list = get_drivers_data()
seasons = list(range(2018, 2026))


# --- Sidebar Filters ---
st.sidebar.header("Driver Selector")
driver = st.sidebar.selectbox("Choose Driver", options=drivers_list)  # Example list
show_driver_button = st.sidebar.button('Show Driver Details')

if show_driver_button:
    # with st.spinner(f"Loading stats for {driver}..."):
    # driver_stats = get_driver_stats(driver)
    driver_results = get_driver_results(driver)

    st.dataframe(driver_results)

    st.header(f"Stats for {driver}")

    profile_col1, profile_col2 = st.columns([1,3])

    with profile_col1:
        st.image(get_driver_photo(driver), width=150)

    with profile_col2:
        st.markdown(f'Stats for {driver}')
        kpi_cols = st.columns(3)
        kpi_cols[0].metric('Total Races', driver_stats['Races'])
        kpi_cols[1].metric('Finished', driver_stats['Finished'])
        kpi_cols[2].metric('DNFs', driver_stats['DNFs'])

        kpi_cols2 = st.columns(3)
        kpi_cols2[0].metric('Wins', driver_stats['Wins'])
        kpi_cols2[1].metric('Podiums', driver_stats['Podiums'])
        kpi_cols2[2].metric('Total Points', driver_stats['Points'])

        st.markdown(f'Teams raced for: {driver_stats['Teams']}')