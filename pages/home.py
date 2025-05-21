import streamlit as st
import pandas as pd

from src.data_ingestion.openf1_loader import *

def load_driver_data():
    return get_driver(driver_number=1, session_key='latest')


st.title('F1 Driver-Car Compatibility Dashboard')
st.write('Explore driver synergy using telemetry data.')

driver_df = load_driver_data()
print(driver_df)
st.dataframe(driver_df)