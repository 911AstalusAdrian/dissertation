import streamlit as st

st.set_page_config(page_title="F1 Compatibility App", layout="wide")
st.sidebar.title("Navigation")
st.sidebar.page_link("./app/home.py", label="🏠 Home")
st.sidebar.page_link("app/driverProfile.py", label="👤 Driver Profile")
st.sidebar.page_link("app/compatibilityMatrix.py", label="🔗 Compatibility Matrix")
st.sidebar.page_link("app/telemetryExplorer.py", label="📈 Telemetry Explorer")