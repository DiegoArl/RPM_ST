import streamlit as st
from datetime import datetime
from Scripts.salidas import df_a_excel
from Scripts.carga import leer_archivo_encuesta
from Scripts.encuesta import procesar_flujo_embajadores

st.header("Encuesta Embajadores")

archivo_embajadores = st.file_uploader(
    "Sube el excel con el archivo de embajadores (Ventas, Cuotas, Encuesta, Relacion, CambioRUC)",
    type=["xlsx"],
    key="embajadores_file"
)

if archivo_embajadores:
    try:
        datos = leer_archivo_encuesta(archivo_embajadores)
        st.session_state["embajadores_raw"] = datos
        st.success("Archivo subido correctamente")
    except Exception as e:
        st.error(str(e))

if "embajadores_raw" not in st.session_state:
    st.warning("No se ha cargado el archivo de embajadores")
    st.stop()

if st.button("Procesar archivo"):
    try:
        df_final = procesar_flujo_embajadores(st.session_state["embajadores_raw"])

        if df_final is None or df_final.empty:
            st.error("El procesamiento no generó resultados.")
            st.stop()

        st.session_state["embajadores_df"] = df_final
        st.session_state["embajadores_excel"] = df_a_excel(df_final)

    except Exception as e:
        st.error("Error procesando el archivo. Verifique el formato o cambie de archivo.")
        for key in ["embajadores_raw", "embajadores_df", "embajadores_excel"]:
            st.session_state.pop(key, None)
        st.stop()

if "embajadores_df" not in st.session_state:
    st.stop()

df_final = st.session_state["embajadores_df"]
excel_file = st.session_state["embajadores_excel"]

st.subheader("Archivo Embajadores")
st.write(f"Filas: {df_final.shape[0]} | Columnas: {df_final.shape[1]}")
st.dataframe(df_final.head())

fecha_actual = datetime.now()
nombre_archivo = f"Embajadores_Procesado_{fecha_actual.strftime('%d%m%Y')}.xlsx"

st.download_button(
    label="Descargar Excel",
    data=excel_file,
    file_name=nombre_archivo,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)