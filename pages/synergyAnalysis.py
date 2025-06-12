import streamlit as st


from src.data_ingestion.openf1_loader import get_distinct_drivers

st.title("Driver-Car Synergy Analysis")

driver = st.selectbox('Select Driver', get_distinct_drivers())