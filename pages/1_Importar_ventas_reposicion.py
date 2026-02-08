# pages/1_Importar_ventas_reposicion.py
import streamlit as st
import pandas as pd
from utils import (
    init_state, ensure_style, load_repo_data, read_petition_excel,
    build_catalog_indexes, match_petition_to_catalog, add_to_cart
)

st.set_page_config(page_title="Importar ventas/reposición", page_icon="📤", layout="wide")
ensure_style()
init_state()
load_repo_data()
st.session_state.setdefault("import_done_for", "")

st.markdown("# 1 · Importar ventas/reposición (opcional)")
st.markdown("<div class='small'>Sube el Excel de ventas/reposición para precargar el <b>carrito importado</b>. Si no lo subes, puedes añadir todo manualmente.</div>", unsafe_allow_html=True)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

cat = st.session_state.catalog_df
idx_exact, idx_ref_color, idx_ref_talla, idx_ref = build_catalog_indexes(cat)

c1, c2 = st.columns([2.2, 1.0])
with c1:
    petition_file = st.file_uploader("Excel de ventas/reposición", type=["xlsx", "xls"], key="u_petition")
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

if petition_file is None:
    if petition_file is None:
    st.info("No has subido fichero. Este paso es opcional — puedes continuar a **2 · Selección manual**.")
else:
    file_id = f"{petition_file.name}:{petition_file.size}"
    if st.session_state.import_done_for != file_id:
        with st.spinner("Procesando importación…"):
            pet_df = read_petition_excel(petition_file.getvalue())
            matched, pending = match_petition_to_catalog(
                pet_df, idx_exact, idx_ref_color, idx_ref_talla, idx_ref
            )

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

            st.session_state.import_done_for = file_id

        st.success("Importación aplicada.")

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
st.info("Siguiente: ve a **2 · Selección manual** para ajustar con el grid.")

from utils import nav_buttons

nav_buttons(
    prev_page="app.py",
    next_page="pages/2_Seleccion_manual.py",
    next_label="Continuar a selección manual →"
)
