# pages/1_Importar_ventas_reposicion.py
import hashlib
import streamlit as st
import pandas as pd
from utils import (
    init_state,
    ensure_style,
    load_repo_data,
    read_petition_excel,
    build_catalog_indexes,
    match_petition_to_catalog,
    add_to_cart,
)

st.set_page_config(page_title="Importar ventas/reposición", page_icon="📤", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.session_state.setdefault("import_done_hash", "")

st.markdown("# 1 · Importar ventas/reposición (opcional)")
st.markdown(
    "<div class='small'>Sube el Excel para precargar el <b>carrito importado</b>. "
    "Si no lo subes, puedes seguir a selección manual.</div>",
    unsafe_allow_html=True,
)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

cat = st.session_state.catalog_df
idx_exact, idx_ref_color, idx_ref_talla, idx_ref = build_catalog_indexes(cat)

c1, c2 = st.columns([2.2, 1.2])
with c1:
    petition_file = st.file_uploader("Excel de ventas/reposición", type=["xlsx", "xls"], key="u_petition")
with c2:
    if st.button("Vaciar carrito importado", use_container_width=True):
        st.session_state.carrito_import = {}
        st.session_state.pending_rows = []
        st.session_state.last_import_stats = None
        st.session_state.import_done_hash = ""

process_now = st.button("Procesar ahora", type="primary", use_container_width=True)

def process_bytes(xlsx_bytes: bytes):
    pet_df = read_petition_excel(xlsx_bytes)
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

if petition_file is None:
    st.info("No has subido fichero. Este paso es opcional.")
else:
    b = petition_file.getvalue()
    # A veces en móvil el primer run devuelve bytes vacíos: no procesamos hasta tener contenido real
    if b and len(b) > 1000:
        h = hashlib.sha256(b).hexdigest()

        # Auto-procesa una sola vez por fichero
        if st.session_state.import_done_hash != h:
            with st.spinner("Procesando importación…"):
                process_bytes(b)
                st.session_state.import_done_hash = h
            st.success("Importación aplicada.")
        elif process_now:
            # Si el usuario fuerza reprocesado
            with st.spinner("Reprocesando…"):
                process_bytes(b)
            st.success("Reprocesado aplicado.")
    else:
        st.warning("Archivo detectado pero aún no cargado completamente. Pulsa de nuevo o usa “Procesar ahora”.")

if st.session_state.get("last_import_stats"):
    s = st.session_state.last_import_stats
    m1, m2, m3 = st.columns(3)
    m1.metric("Líneas matcheadas", s["matched_lines"])
    m2.metric("Pendientes", s["pending_lines"])
    m3.metric("Líneas añadidas", s["added_lines"])

if st.session_state.get("pending_rows"):
    st.markdown("### Pendientes")
    st.dataframe(pd.DataFrame(st.session_state.pending_rows), use_container_width=True)

st.markdown("<hr/>", unsafe_allow_html=True)
st.page_link("pages/2_Seleccion_manual.py", label="Continuar a 2 · Selección manual →", use_container_width=True)
st.page_link("app.py", label="← Volver a datos del pedido", use_container_width=True)
