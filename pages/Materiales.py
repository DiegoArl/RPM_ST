import streamlit as st
import hashlib
from Scripts.carga import leer_archivo_materiales, leer_archivo_materiales_datanest
from Scripts.material import procesar_flujo_materiales_datanest

st.header("Materiales")

def file_hash(file):
    return hashlib.md5(file.getvalue()).hexdigest()

def archivos_materiales_cargados():
    requeridos = [
        "codificacion_df"
    ]
    return all(k in st.session_state for k in requeridos)

archivo_codificacion = st.file_uploader(
    "Subir Base Datanest",
    type=["csv", "xlsx"],
    key="codificacion_file"
)

if archivo_codificacion:
    hash_actual = file_hash(archivo_codificacion)

    if st.session_state.get("archivo_hash") != hash_actual:
        codificacion = leer_archivo_materiales_datanest(archivo_codificacion)
        _, df_out_c = procesar_flujo_materiales_datanest(codificacion)

        st.session_state["codificacion_df"] = df_out_c
        st.session_state["archivo_hash"] = hash_actual

if "codificacion_df" in st.session_state:
    df = st.session_state["codificacion_df"]
    st.write(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
    st.dataframe(df)
else:
    st.info("Carga un archivo")