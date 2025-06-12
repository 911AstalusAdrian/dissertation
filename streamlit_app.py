import streamlit as st
import fastf1

st.set_page_config(page_title="F1 Compatibility App", layout="wide")

fastf1.Cache.set_enabled()
pages = [st.Page('pages/home.py', title = "Home"),
         st.Page('pages/driverProfile.py', title = 'Driver Profile'),
         st.Page('pages/compatibilityMatrix.py', title = 'Compatibility Matrix'),
         st.Page('pages/telemetryExplorer.py', title = 'Telemetry Explorer')]

pg = st.navigation(pages)
pg.run()