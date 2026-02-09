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
    "<div class='small'>Sube el Excel para precargar el <b>carrito importado</b>. "
    "En móvil, el archivo puede tardar 1–2 reruns en estar disponible; esta pantalla lo gestiona sola.</div>",
    unsafe_allow_html=True,
)

# --- estado para upload robusto ---
st.session_state.setdefault("petition_bytes", None)
st.session_state.setdefault("petition_name", "")
st.session_state.setdefault("petition_hash", "")
st.session_state.setdefault("import_hash_done", "")
st.session_state.setdefault("pending_rows", [])
st.session_state.setdefault("last_import_stats", None)
st.session_state.setdefault("carrito_import", {})

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

cat = st.session_state.catalog_df
idx_exact, idx_ref_color, idx_ref_talla, idx_ref = build_catalog_indexes(cat)

def _capture_upload():
    """Captura bytes del uploader en session_state al cambiar el archivo."""
    uf = st.session_state.get("u_petition")
    if uf is None:
        st.session_state.petition_bytes = None
        st.session_state.petition_name = ""
        st.session_state.petition_hash = ""
        return

    try:
        b = uf.getvalue()
    except Exception:
        b = None

    # Si en móvil llega vacío, no sobreescribimos por None; esperamos próximo rerun
    if b and len(b) > 1000:
        st.session_state.petition_bytes = b
        st.session_state.petition_name = getattr(uf, "name", "") or ""
        st.session_state.petition_hash = hashlib.sha256(b).hexdigest()

def _process_bytes(b: bytes):
    pet_df = read_petition_excel(b)
    matched, pending = match_petition_to_catalog(pet_df, idx_exact, idx_ref_color, idx_ref_talla, idx_ref)

    added_lines = 0
    for m in matched:
        # m debe traer EAN/Referencia/Nombre/Color/Talla/Cantidad según tu pipeline
        add_to_cart(st.session_state.carrito_import, m, int(m["Cantidad"]))
        added_lines += 1

    st.session_state.pending_rows = pending
    st.session_state.last_import_stats = {
        "matched_lines": len(matched),
        "pending_lines": len(pending),
        "added_lines": added_lines,
    }

# --- UI ---
top1, top2, top3 = st.columns([2.2, 1.1, 1.1])

with top1:
    st.file_uploader(
        "Excel de ventas/reposición",
        type=["xlsx", "xls"],
        key="u_petition",
        on_change=_capture_upload,
    )

with top2:
    if st.button("Vaciar carrito importado", use_container_width=True):
        st.session_state.carrito_import = {}
        st.session_state.last_import_stats = None

with top3:
    if st.button("Vaciar pendientes", use_container_width=True):
        st.session_state.pending_rows = []

# En móvil, a veces on_change no captura a la primera: intentamos capturar también en cada rerun si hay uploader
if st.session_state.get("petition_bytes") is None and st.session_state.get("u_petition") is not None:
    _capture_upload()

b = st.session_state.get("petition_bytes")
h = st.session_state.get("petition_hash")

# Botón manual (respaldo)
process_manual = st.button("Procesar importación", type="primary", use_container_width=True)

if b is None:
    if st.session_state.get("u_petition") is None:
        st.info("No has subido fichero. Este paso es opcional — puedes continuar a **2 · Selección manual**.")
    else:
        st.warning("Archivo detectado, pero aún no está listo (móvil). Espera un momento o vuelve a pulsar Procesar.")
else:
    # Auto-procesa una sola vez por fichero (hash)
    if h and st.session_state.import_hash_done != h:
        with st.spinner("Procesando importación…"):
            _process_bytes(b)
            st.session_state.import_hash_done = h
        st.success("Importación aplicada.")
    elif process_manual:
        with st.spinner("Reprocesando…"):
            _process_bytes(b)
        st.success("Reprocesado aplicado.")

# Stats
if st.session_state.get("last_import_stats"):
    s = st.session_state.last_import_stats
    m1, m2, m3 = st.columns(3)
    m1.metric("Líneas matcheadas", s["matched_lines"])
    m2.metric("Pendientes", s["pending_lines"])
    m3.metric("Líneas añadidas", s["added_lines"])

# Pendientes
if st.session_state.get("pending_rows"):
    st.markdown("### Pendientes")
    st.dataframe(pd.DataFrame(st.session_state.pending_rows), use_container_width=True, hide_index=True)

st.markdown("<hr/>", unsafe_allow_html=True)
st.page_link("pages/2_Seleccion_manual.py", label="Continuar a 2 · Selección manual →", use_container_width=True)
st.page_link("app.py", label="← Volver a 0 · Datos del pedido", use_container_width=True)
