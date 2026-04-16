import streamlit as st
from datetime import datetime
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo_materiales, leer_archivo_materiales_datanest
from Scripts.material import procesar_flujo_materiales_datanest

st.header("Materiales")

def archivos_materiales_cargados():
    requeridos = ["codificacion_raw", "materiales_raw"]
    return all(k in st.session_state for k in requeridos)

archivo_codificacion = st.file_uploader(
    "Subir Base Datanest",
    type=["csv", "xlsx"],
    key="codificacion_file"
)

if archivo_codificacion:
    try:
        st.session_state["codificacion_raw"] = leer_archivo_materiales_datanest(archivo_codificacion)
        st.success("Base Datanest cargada correctamente")
    except Exception as e:
        st.error(str(e))

archivo_materiales = st.file_uploader(
    "Subir Materiales",
    type=["csv", "xlsx"],
    key="materiales_file"
)

if archivo_materiales:
    try:
        st.session_state["materiales_raw"] = leer_archivo_materiales(archivo_materiales)
        st.success("Materiales cargados correctamente")
    except Exception as e:
        st.error(str(e))

listo = archivos_materiales_cargados()

if not listo:
    st.warning("Faltan archivos por cargar")

if st.button("Procesar archivos", disabled=not listo):
    try:
        df_final = procesar_flujo_materiales_datanest(
            st.session_state["codificacion_raw"],
            st.session_state["materiales_raw"]
        )

        if df_final is None or df_final.empty:
            st.error("El procesamiento no generó resultados.")
            st.stop()

        st.session_state["materiales_df"] = df_final
        st.session_state["materiales_excel"] = df_a_excel(df_final)

    except Exception as e:
        st.error("Error procesando los archivos. Verifique el formato o cambie de archivo.")
        for key in ["codificacion_raw", "materiales_raw", "materiales_df", "materiales_excel"]:
            st.session_state.pop(key, None)
        st.stop()

if "materiales_df" not in st.session_state:
    st.stop()

df_final = st.session_state["materiales_df"]
excel_file = st.session_state["materiales_excel"]

st.subheader("Materiales Procesados")
st.write(f"Filas: {df_final.shape[0]} | Columnas: {df_final.shape[1]}")
st.dataframe(df_final.head())

fecha_actual = datetime.now()
nombre_archivo = f"Materiales_Procesado.xlsx"

st.download_button(
    label="Descargar Excel",
    data=excel_file,
    file_name=nombre_archivo,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)