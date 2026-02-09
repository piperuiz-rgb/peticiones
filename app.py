# app.py
import streamlit as st
from utils import (
    init_state,
    ensure_style,
    load_repo_data,
    ORIGIN_OPTIONS,
    DEST_OPTIONS,
    warehouse_fmt,
)

st.set_page_config(page_title="Peticiones almacenes", page_icon="📦", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 0 · Datos del pedido")
st.markdown(
    "<div class='small'>Catálogo y plantilla se cargan automáticamente desde el repositorio.</div>",
    unsafe_allow_html=True,
)

# -----------------------------
# Validación catálogo
# -----------------------------
if not st.session_state.get("cat_loaded"):
    st.error("No se encontró **catalogue.xlsx** en la raíz del repositorio.")
    st.stop()

# -----------------------------
# Cabecera del pedido
# -----------------------------
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 2.0])

with c1:
    st.session_state.fecha = st.date_input(
        "Fecha",
        value=st.session_state.fecha,
    )

with c2:
    st.session_state.origen = st.selectbox(
        "Almacén de origen",
        ORIGIN_OPTIONS,
        index=ORIGIN_OPTIONS.index(st.session_state.origen)
        if st.session_state.origen in ORIGIN_OPTIONS
        else 0,
        format_func=warehouse_fmt,
    )

with c3:
    st.session_state.destino = st.selectbox(
        "Almacén de destino",
        DEST_OPTIONS,
        index=DEST_OPTIONS.index(st.session_state.destino)
        if st.session_state.destino in DEST_OPTIONS
        else 0,
        format_func=warehouse_fmt,
    )

with c4:
    st.session_state.ref_peticion = st.text_input(
        "Referencia de la petición (se exporta en Observaciones)",
        value=st.session_state.ref_peticion,
        placeholder="Ej: PET-2026-02-IBIZA",
    )

# -----------------------------
# Bloqueo: origen = destino
# -----------------------------
if st.session_state.origen == st.session_state.destino:
    st.warning("El almacén de origen y destino no pueden ser el mismo. Cambia uno de los dos para continuar.")
    st.stop()

st.markdown("<hr/>", unsafe_allow_html=True)

# -----------------------------
# Aviso plantilla
# -----------------------------
if st.session_state.get("tpl_bytes") is None:
    st.warning(
        "No se encontró **plantilla_pedido.xlsx** en la raíz del repositorio. "
        "Podrás trabajar, pero no exportar."
    )

# -----------------------------
# Navegación
# -----------------------------
st.markdown("### Siguiente paso")

st.page_link(
    "pages/1_Importar_ventas_reposicion.py",
    label="Continuar a 1 · Importar ventas/reposición →",
    use_container_width=True,
)

st.page_link(
    "pages/2_Seleccion_manual.py",
    label="Saltar importación y pasar a 2 · Selección manual →",
    use_container_width=True,
)
