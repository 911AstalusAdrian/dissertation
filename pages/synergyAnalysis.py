import streamlit as st


from src.data_ingestion.openf1_loader import get_fulltime_drivers, get_teams_for_driver

def get_list_of_drivers():
    distinct_drivers_df = get_fulltime_drivers()

    return distinct_drivers_df['full_name'].to_list()

def get_driver_teams(driver_name):
    return get_teams_for_driver(driver_name)

st.title("Driver-Car Synergy Analysis")

driver = st.selectbox('Select Driver', options=get_list_of_drivers())

if driver:
    st.selectbox('Select Team', options=get_driver_teams(driver))