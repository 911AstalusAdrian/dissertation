import streamlit as st

st.set_page_config(page_title="F1 Compatibility App", layout="wide")
st.sidebar.title("Navigation")
st.sidebar.page_link("app/Home.py", label="🏠 Home")
st.sidebar.page_link("app/DriverProfile.py", label="👤 Driver Profile")
st.sidebar.page_link("app/CompatibilityMatrix.py", label="🔗 Compatibility Matrix")
st.sidebar.page_link("app/TelemetryExplorer.py", label="📈 Telemetry Explorer")