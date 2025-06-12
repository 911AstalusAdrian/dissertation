import streamlit as st
import fastf1

st.set_page_config(page_title="F1 Compatibility App", layout="wide")

pages = [st.Page('pages/home.py', title = "Home"),
         st.Page('pages/driverProfile.py', title = 'Driver Profile'),
         st.Page('pages/synergyAnalysis.py', title = 'Synergy Analysis'),
         st.Page('pages/telemetryExplorer.py', title = 'Telemetry Explorer')]

pg = st.navigation(pages)
pg.run()