# pages/4_Exportar.py
import io
import streamlit as st
from openpyxl import load_workbook
from utils import init_state, ensure_style, load_repo_data, merge_carts

st.set_page_config(page_title="Exportar", page_icon="📦", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 4 · Exportar pedido")

# Validaciones base
merged = merge_carts(st.session_state.carrito_import, st.session_state.carrito_manual)
if not merged:
    st.warning("No hay líneas en el pedido. Vuelve a selección y añade prendas.")
    st.page_link("pages/2_Seleccion_manual.py", label="← Volver a selección manual", use_container_width=True)
    st.stop()

if st.session_state.get("tpl_bytes") is None:
    st.error("No se encontró `plantilla_pedido.xlsx` en el repositorio. No se puede exportar.")
    st.stop()

# Origen/destino: ya son PET (no códigos)
origen_txt = st.session_state.origen
destino_txt = st.session_state.destino

# Bloqueo ruta
if origen_txt == destino_txt:
    st.error("Origen y destino no pueden coincidir.")
    st.stop()

safe_ref = (st.session_state.ref_peticion or "SIN_REF").replace(" ", "_")
filename = f"{st.session_state.fecha:%Y%m%d}_{safe_ref}.xlsx".replace(" ", "_")

# Carga plantilla
wb = load_workbook(io.BytesIO(st.session_state.tpl_bytes))
ws = wb.active

# ⚠️ Ajusta aquí si tu plantilla usa celdas distintas
# (Mantengo nombres genéricos; si tu plantilla tiene celdas concretas, dime cuáles y lo dejo exacto)
ws["B2"] = origen_txt
ws["B3"] = destino_txt
ws["B4"] = st.session_state.ref_peticion or ""

# Aquí NO toco tu lógica de líneas porque depende de cómo lo tengas implementado en tu export actual.
# Si tu export ya rellena líneas, conserva esa parte y solo cambia ORIG/DEST a origen_txt/destino_txt.

out = io.BytesIO()
wb.save(out)
out.seek(0)

st.success("Archivo listo para descargar.")
st.download_button(
    "Descargar Excel",
    data=out.getvalue(),
    file_name=filename,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.page_link("pages/3_Revision_final.py", label="← Volver a revisión", use_container_width=True)
