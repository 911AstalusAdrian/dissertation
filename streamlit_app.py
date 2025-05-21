import streamlit as st

st.set_page_config(page_title="F1 Compatibility App", layout="wide")
st.sidebar.title("Navigation")
st.page_link('pages/home.py', label="🏠 Home")
st.page_link("app/driverProfile.py", label="👤 Driver Profile")
st.page_link("app/compatibilityMatrix.py", label="🔗 Compatibility Matrix")
st.page_link("app/telemetryExplorer.py", label="📈 Telemetry Explorer")