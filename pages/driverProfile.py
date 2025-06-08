import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import timedelta
from src.data_ingestion.openf1_loader import *
from src.data_ingestion.fastf1_loader import get_kpis_from_session, get_session_top5_drivers_laps, get_session_tyre_distribution
from src.utils.df_utils import format_laptime


# --- Layout ---
st.title("\U0001F3CE Driver Profile")

# --- Sidebar Filters ---
st.sidebar.header("Driver Selector")
driver = st.sidebar.selectbox("Choose Driver", options=["VER", "HAM", "LEC", "SAI", "NOR", "RUS"])  # Example list
season = st.sidebar.selectbox("Season", options=[2021, 2022, 2023, 2024])
session_type = st.sidebar.selectbox("Session Type", options=["RACE", "QUALIFYING", "PRACTICE"])
round_number = st.sidebar.number_input("Round (optional)", min_value=1, max_value=25, step=1)