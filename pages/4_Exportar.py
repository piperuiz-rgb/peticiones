# pages/4_Exportar.py
import streamlit as st
import pandas as pd
from utils import init_state, ensure_style, load_repo_data, merge_carts, cart_to_df, export_to_template_xlsx, openpyxl

st.set_page_config(page_title="Exportar", page_icon="⬇️", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 4 · Exportar pedido")
st.markdown("<div class='small'>Exporta la fusión de carritos a <b>plantilla_pedido.xlsx</b> (Observaciones = referencia de petición).</div>", unsafe_allow_html=True)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

if openpyxl is None:
    st.error("No se puede exportar a plantilla: falta la dependencia 'openpyxl'.")
    st.stop()

tpl_bytes = st.session_state.get("tpl_bytes")
if tpl_bytes is None:
    st.error("No se encontró `plantilla_pedido.xlsx` en la raíz del repositorio.")
    st.stop()

car_merge = merge_carts(st.session_state.carrito_import, st.session_state.carrito_manual)
car_merge_df = cart_to_df(car_merge)[["EAN","Ref","Nom","Col","Tal","Cantidad"]].rename(
    columns={"Ref":"Referencia","Nom":"Nombre","Col":"Color","Tal":"Talla"}
)

if car_merge_df.empty:
    st.info("No hay líneas para exportar.")
    st.stop()

export_lines = car_merge_df[["EAN","Cantidad"]].copy()
export_lines["Cantidad"] = pd.to_numeric(export_lines["Cantidad"], errors="coerce").fillna(0).astype(int)
export_lines = export_lines[export_lines["Cantidad"] > 0].reset_index(drop=True)

filename = st.text_input(
    "Nombre archivo",
    value=f"pedido_{st.session_state.origen}_a_{st.session_state.destino}_{st.session_state.fecha.isoformat()}.xlsx".replace(" ", "_"),
)

st.markdown("### Resumen")
st.write(
    f"- Fecha: **{st.session_state.fecha.isoformat()}**\n"
    f"- Origen: **{st.session_state.origen}**\n"
    f"- Destino: **{st.session_state.destino}**\n"
    f"- Observaciones: **{st.session_state.ref_peticion or '-'}**\n"
    f"- Líneas: **{len(export_lines)}**"
)

try:
    out_bytes = export_to_template_xlsx(
        df_lines=export_lines,
        fecha=st.session_state.fecha,
        origen=st.session_state.origen,
        destino=st.session_state.destino,
        observaciones=st.session_state.ref_peticion or "",
        template_bytes=tpl_bytes,
    )
    st.download_button(
        "Descargar pedido (XLSX)",
        data=out_bytes,
        file_name=filename if filename.lower().endswith(".xlsx") else f"{filename}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
    )
except Exception as e:
    st.error(f"Error exportando: {e}")
