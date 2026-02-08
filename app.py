# app.py
import streamlit as st
from utils import init_state, ensure_style, load_repo_data, ORIGIN_OPTIONS, DEST_OPTIONS

st.set_page_config(page_title="Peticiones almacenes", page_icon="📦", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 0 · Datos del pedido")
st.markdown("<div class='small'>Catálogo y plantilla se cargan automáticamente desde el repositorio.</div>", unsafe_allow_html=True)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró **catalogue.xlsx** en la raíz del repositorio (o tiene columnas incorrectas).")
    st.stop()

c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 2.0])
with c1:
    st.session_state.fecha = st.date_input("Fecha", value=st.session_state.fecha)
with c2:
    st.session_state.origen = st.selectbox(
        "Almacén de origen",
        ORIGIN_OPTIONS,
        index=ORIGIN_OPTIONS.index(st.session_state.origen) if st.session_state.origen in ORIGIN_OPTIONS else 0,
    )
with c3:
    st.session_state.destino = st.selectbox(
        "Almacén de destino",
        DEST_OPTIONS,
        index=DEST_OPTIONS.index(st.session_state.destino) if st.session_state.destino in DEST_OPTIONS else 0,
    )
with c4:
    st.session_state.ref_peticion = st.text_input(
        "Referencia de la petición (se exporta en Observaciones)",
        value=st.session_state.ref_peticion,
        placeholder="Ej: PET-2026-02-08-MARBELLA",
    )

st.markdown("<hr/>", unsafe_allow_html=True)

if st.session_state.get("tpl_bytes") is None:
    st.warning("No se encontró **plantilla_pedido.xlsx** en la raíz del repositorio. Podrás trabajar, pero no exportar.")

st.info("Siguiente: ve a **1 · Importar ventas/reposición** en el menú de la izquierda (opcional).")

from utils import nav_buttons

nav_buttons(
    prev_page=None,
    next_page="pages/1_Importar_ventas_reposicion.py",
    next_label="Confirmar datos y continuar →"
)
