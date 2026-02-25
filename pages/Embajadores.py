import streamlit as st
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo_encuesta
from Scripts.encuesta import procesar_flujo_embajadores

st.markdown("""
<style>
[data-testid="stSidebarNav"] ul li:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)


st.header("Encuesta Embajadores")


archivo_embajadores = st.file_uploader(
    "Sube el excel con el archivo de embajadores (Ventas, Cuotas, Encuesta, Relacion, CambioRUC)",
    type=["xlsx"]
)


@st.cache_data
def procesar_embajadores(df):
    return procesar_flujo_embajadores(df)


@st.cache_data
def generar_excel(df):
    return df_a_excel(df)


if archivo_embajadores and "embajadores_raw" not in st.session_state:

    try:

        datos = leer_archivo_encuesta(archivo_embajadores)
        st.session_state.embajadores_raw = datos

        df_final = procesar_embajadores(datos)

        if df_final is None or df_final.empty:
            st.error("El procesamiento no generó resultados")
            st.stop()

        st.session_state.embajadores_df = df_final
        st.session_state.embajadores_excel = generar_excel(df_final)

        st.success("Archivo procesado correctamente")

    except Exception as e:

        st.error("Error procesando el archivo")
        st.error(str(e))
        st.stop()


if "embajadores_df" not in st.session_state:
    st.warning("No se ha cargado el archivo de embajadores")
    st.stop()


df_final = st.session_state.embajadores_df
excel_file = st.session_state.embajadores_excel


st.subheader("Archivo Embajadores")

st.write(
    f"Filas: {df_final.shape[0]} | Columnas: {df_final.shape[1]}"
)

st.dataframe(df_final.head())


st.download_button(
    label="Descargar Excel",
    data=excel_file,
    file_name="Embajadores_Procesado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)