import streamlit as st

if "seccion" not in st.session_state:
    st.session_state["seccion"] = None

embajadores_page = st.Page("pages/Embajadores.py", title="Embajadores", icon="👷‍♂️")
rpm_page = st.Page("pages/RPM.py", title="RPM", icon="🚧")
materiales_page = st.Page("pages/Materiales.py", title="Materiales", icon="🏖️")
dashboard_materiales_page = st.Page("pages/Dashboard_Materiales.py", title="Dashboard Materiales", icon="📊")
inicio_page = st.Page("pages/Inicio.py", title="Inicio", icon="🏠")

if st.session_state["seccion"] is None:
    pg = st.navigation([inicio_page], position="hidden")
    pg.run()
    st.title("Bienvenido")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋  Generación de reportes", use_container_width=True):
            st.session_state["seccion"] = "reportes"
            st.rerun()
    with col2:
        if st.button("📊  Visualización de dashboard", use_container_width=True):
            st.session_state["seccion"] = "dashboard"
            st.rerun()
    st.stop()

if st.session_state["seccion"] == "reportes":
    pages = {"Generar Reportes": [rpm_page, embajadores_page, materiales_page]}
else:
    pages = {"Dashboard": [dashboard_materiales_page]}

with st.sidebar:
    st.divider()
    if st.button("⬅  Volver al inicio"):
        st.session_state["seccion"] = None
        st.rerun()

pg = st.navigation(pages)
pg.run()