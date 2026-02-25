import io
import pandas as pd

def df_a_excel(df):
    if df is None or df.empty:
        raise ValueError("DataFrame vacío: no se puede exportar")

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultado")

    buffer.seek(0)
    return buffer

def df_a_csv(df):
    if df is None or df.empty:
        raise ValueError("DataFrame vacío: no se puede exportar")

    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")

    buffer.seek(0)
    return buffer