import streamlit as st

embajadores_page = st.Page("pages/Embajadores.py", title="Embajadores", icon="👷‍♂️")
rpm_page = st.Page("pages/RPM.py", title="RPM", icon="🚧")
materiales_page = st.Page("pages/Materiales.py", title="Materiales", icon="🏖️")

dashboard_materiales_page = st.Page("pages/Dashboard_Materiales.py", title="Dashboard Materiales", icon="📊")

pg = st.navigation(
        {
            "Generar Reportes": [rpm_page, embajadores_page, materiales_page], 
            "Dashboard": [dashboard_materiales_page]
        }
    )

pg.run()