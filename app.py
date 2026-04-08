import streamlit as st

embajadores_page = st.Page("pages/Embajadores.py", title="Embajadores", icon="🚚")
rpm_page = st.Page("pages/RPM.py", title="RPM", icon="🗺️")

pg = st.navigation(
        {
            "Reportes": [rpm_page, embajadores_page], 
        }
    )

pg.run()