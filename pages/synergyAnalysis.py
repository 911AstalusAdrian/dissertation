import streamlit as st


from src.data_ingestion.openf1_loader import get_fulltime_drivers

def get_list_of_drivers():
    distinct_drivers_df = get_fulltime_drivers()

    return distinct_drivers_df['full_name'].to_list()


st.title("Driver-Car Synergy Analysis")

driver = st.selectbox('Select Driver', options=get_list_of_drivers())