import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import timedelta
from src.data_ingestion.openf1_loader import *
from src.data_ingestion.fastf1_loader import get_distinct_drivers, get_driver_stats_multiseason
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
def get_driver_photo(driver_name):
    pass

drivers_list = get_drivers_data()
seasons = list(range(2018, 2026))


# --- Sidebar Filters ---
st.sidebar.header("Driver Selector")
driver = st.sidebar.selectbox("Choose Driver", options=drivers_list)  # Example list
show_driver_button = st.sidebar.button('Show Driver Details')

if show_driver_button:
    with st.spinner(f"Loading stats for {driver}..."):
        driver_stats = get_driver_stats(driver)

    st.header(f"Stats for {driver}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Races", driver_stats['Races'])
    col1.metric("Finished Races", driver_stats['Finished'])
    col1.metric("DNFs", driver_stats['DNFs'])

    col2.metric("Wins", driver_stats['Wins'])
    col2.metric("Podiums", driver_stats['Podiums'])

    col3.metric("Total Points", driver_stats['Points'])
    col3.metric("Avg Points per Race", driver_stats['Avg Points/Race'])
    # load_data regarding the driver using openF1 API '/driver'
    # make sure to modify the last name to be all caps