import streamlit as st

st.set_page_config(page_title="F1 Compatibility App", layout="wide")


pages = {
    "🏠 Home": [st.Page('pages/home.py', title="Home")],
    "Driver Profile": [st.Page('pages/driverProfile.py', title="Driver Profile")]
}

pg = st.navigation(pages)
pg.run()

# st.page_link('pages/home.py', label="🏠 Home")
# st.page_link("app/driverProfile.py", label="👤 Driver Profile")
# st.page_link("app/compatibilityMatrix.py", label="🔗 Compatibility Matrix")
# st.page_link("app/telemetryExplorer.py", label="📈 Telemetry Explorer")