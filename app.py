embajadores_page = st.Page("pages/Embajadores.py", title="Embajadores", icon="👷‍♂️")
rpm_page = st.Page("pages/RPM.py", title="RPM", icon="🚧")
materiales_page = st.Page("pages/Materiales.py", title="Materiales", icon="🏖️")

pg = st.navigation(
        {
            "Reportes": [rpm_page, embajadores_page], 
        }
    )

pg.run()