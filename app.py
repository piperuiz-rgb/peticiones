# app.py
from datetime import date
import streamlit as st
from utils import init_state, ensure_style, load_catalog_from_sidebar, ORIGIN_OPTIONS, DEST_OPTIONS

st.set_page_config(page_title="Peticiones almacenes", page_icon="📦", layout="wide")
ensure_style()
init_state()
load_catalog_from_sidebar()

st.markdown("# 0 · Datos del pedido")
st.markdown("<div class='small'>Completa los datos base antes de importar/añadir prendas.</div>", unsafe_allow_html=True)

if not st.session_state.get("cat_loaded"):
    st.warning("Carga el catálogo desde la barra lateral para continuar.")
    st.stop()

c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 2.0])
with c1:
    st.session_state.fecha = st.date_input("Fecha", value=st.session_state.fecha)
with c2:
    st.session_state.origen = st.selectbox("Almacén de origen", ORIGIN_OPTIONS,
        index=ORIGIN_OPTIONS.index(st.session_state.origen) if st.session_state.origen in ORIGIN_OPTIONS else 0)
with c3:
    st.session_state.destino = st.selectbox("Almacén de destino", DEST_OPTIONS,
        index=DEST_OPTIONS.index(st.session_state.destino) if st.session_state.destino in DEST_OPTIONS else 0)
with c4:
    st.session_state.ref_peticion = st.text_input(
        "Referencia de la petición (se exporta en Observaciones)",
        value=st.session_state.ref_peticion,
        placeholder="Ej: PET-2026-02-08-MARBELLA",
    )

st.markdown("<hr/>", unsafe_allow_html=True)
st.info("Siguiente: ve a **Importar petición** en el menú de la izquierda.")
