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

st.markdown("# 1 · Importar ventas/reposición (opcional)")
st.markdown(
    "<div class='small'>Si no funciona, primero confirmamos que el móvil está subiendo bytes reales y que el lector de Excel no falla.</div>",
    unsafe_allow_html=True,
)

st.session_state.setdefault("carrito_import", {})
st.session_state.setdefault("pending_rows", [])
st.session_state.setdefault("last_import_stats", None)
st.session_state.setdefault("import_hash_done", "")

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

cat = st.session_state.catalog_df
idx_exact, idx_ref_color, idx_ref_talla, idx_ref = build_catalog_indexes(cat)

uf = st.file_uploader("Excel de ventas/reposición", type=["xlsx", "xls"], key="u_petition")

colA, colB, colC = st.columns([1.2, 1.2, 1.6])
with colA:
    if st.button("Vaciar carrito importado", use_container_width=True):
        st.session_state.carrito_import = {}
        st.session_state.last_import_stats = None
        st.session_state.import_hash_done = ""
with colB:
    if st.button("Vaciar pendientes", use_container_width=True):
        st.session_state.pending_rows = []
with colC:
    run_import = st.button("Procesar importación", type="primary", use_container_width=True)

# --- Diagnóstico de subida ---
if uf is None:
    st.info("No has subido fichero. Este paso es opcional.")
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.page_link("pages/2_Seleccion_manual.py", label="Continuar a 2 · Selección manual →", use_container_width=True)
    st.page_link("app.py", label="← Volver a 0 · Datos del pedido", use_container_width=True)
    st.stop()

# En móvil: usa buffer (más fiable que getvalue en algunos casos)
try:
    b = bytes(uf.getbuffer())
except Exception:
    # fallback
    b = uf.getvalue()

st.caption(f"Archivo: **{getattr(uf, 'name', '')}** · Tamaño recibido: **{len(b)} bytes**")

if len(b) < 2000:
    st.warning(
        "El fichero aún no ha llegado bien (bytes muy bajos). "
        "En móvil: asegúrate de que el Excel está descargado localmente (no desde vista previa) y prueba de nuevo."
    )

# --- Lectura (preview) ---
try:
    pet_df = read_petition_excel(b)
    st.success(f"Excel leído: {len(pet_df)} filas")
    st.dataframe(pet_df.head(30), use_container_width=True, hide_index=True)
except Exception as e:
    st.error("Falla `read_petition_excel()` al leer el fichero. Error:")
    st.exception(e)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.page_link("pages/2_Seleccion_manual.py", label="Continuar a 2 · Selección manual →", use_container_width=True)
    st.page_link("app.py", label="← Volver a 0 · Datos del pedido", use_container_width=True)
    st.stop()

# --- Procesado (solo si pulsas botón) ---
if run_import:
    h = hashlib.sha256(b).hexdigest()
    if st.session_state.import_hash_done == h:
        st.info("Este fichero ya se procesó. Si quieres reprocesar, cambia el fichero o vacía carrito importado.")
    else:
        try:
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
            st.session_state.import_hash_done = h
            st.success("Importación aplicada.")
        except Exception as e:
            st.error("Falla el matcheo / carga en carrito. Error:")
            st.exception(e)

if st.session_state.get("last_import_stats"):
    s = st.session_state.last_import_stats
    m1, m2, m3 = st.columns(3)
    m1.metric("Líneas matcheadas", s["matched_lines"])
    m2.metric("Pendientes", s["pending_lines"])
    m3.metric("Líneas añadidas", s["added_lines"])

if st.session_state.get("pending_rows"):
    st.markdown("### Pendientes")
    st.dataframe(pd.DataFrame(st.session_state.pending_rows), use_container_width=True, hide_index=True)

st.markdown("<hr/>", unsafe_allow_html=True)
st.page_link("pages/2_Seleccion_manual.py", label="Continuar a 2 · Selección manual →", use_container_width=True)
st.page_link("app.py", label="← Volver a 0 · Datos del pedido", use_container_width=True)
