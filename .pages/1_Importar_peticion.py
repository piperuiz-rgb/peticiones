# pages/1_Importar_peticion.py
import streamlit as st
import pandas as pd
from utils import (
    init_state, ensure_style, load_catalog_from_sidebar, read_petition_excel,
    build_catalog_indexes, match_petition_to_catalog, add_to_cart
)

st.set_page_config(page_title="Importar petición", page_icon="📤", layout="wide")
ensure_style()
init_state()
load_catalog_from_sidebar()

st.markdown("# 1 · Importar petición (Excel)")
st.markdown("<div class='small'>Matchea contra el catálogo y precarga el <b>carrito importado</b>.</div>", unsafe_allow_html=True)

if not st.session_state.get("cat_loaded"):
    st.warning("Carga el catálogo desde la barra lateral para continuar.")
    st.stop()

cat = st.session_state.catalog_df
idx_exact, idx_ref_color, idx_ref_talla, idx_ref = build_catalog_indexes(cat)

c1, c2 = st.columns([2.2, 1.0])
with c1:
    petition_file = st.file_uploader("Excel de petición", type=["xlsx", "xls"], key="u_petition")
with c2:
    a, b = st.columns(2)
    with a:
        if st.button("Vaciar carrito importado", use_container_width=True):
            st.session_state.carrito_import = {}
            st.session_state.pending_rows = []
            st.session_state.last_import_stats = None
    with b:
        if st.button("Vaciar pendientes", use_container_width=True):
            st.session_state.pending_rows = []

if petition_file is not None and st.button("Procesar importación", type="primary"):
    pet_df = read_petition_excel(petition_file.getvalue())
    matched, pending = match_petition_to_catalog(pet_df, idx_exact, idx_ref_color, idx_ref_talla, idx_ref)

    added_lines = 0
    for m in matched:
        add_to_cart(st.session_state.carrito_import, m, int(m["Cantidad"]))
        added_lines += 1

    st.session_state.pending_rows = pending
    st.session_state.last_import_stats = {
        "matched_lines": len(matched),
        "pending_lines": len(pending),
        "added_lines": added_lines,
    }

if st.session_state.last_import_stats:
    s = st.session_state.last_import_stats
    m1, m2, m3 = st.columns(3)
    m1.metric("Líneas matcheadas", s["matched_lines"])
    m2.metric("Pendientes", s["pending_lines"])
    m3.metric("Líneas añadidas", s["added_lines"])

if st.session_state.pending_rows:
    st.markdown("### Pendientes")
    st.dataframe(pd.DataFrame(st.session_state.pending_rows), use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)
st.info("Siguiente: ve a **Selección manual** para ajustar con el grid.")
