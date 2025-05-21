import streamlit as st

st.set_page_config(page_title="F1 Compatibility App", layout="wide")


pages = [st.Page('pages/home.py', title = "Home"),
         st.Page('pages/driverProfile.py', title = 'Driver Profile'),
         st.Page('pages/compatibilityMatrix.py', title = 'Compatibility Matrix'),
         st.Page('pages/telemetryExplorer.py', title = 'Telemetry Explorer')]

pg = st.navigation(pages)
pg.run()

# st.page_link('pages/home.py', label="🏠 Home")
# st.page_link("app/driverProfile.py", label="👤 Driver Profile")
# st.page_link("app/compatibilityMatrix.py", label="🔗 Compatibility Matrix")
# st.page_link("app/telemetryExplorer.py", label="📈 Telemetry Explorer")