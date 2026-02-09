# app.py
import streamlit as st
from utils import (
    init_state,
    ensure_style,
    load_repo_data,
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

# Catálogo obligatorio
if not st.session_state.get("cat_loaded"):
    st.error("No se encontró **catalogue.xlsx** en la raíz del repositorio (o tiene columnas incorrectas).")
    st.stop()

# ✅ Lista cerrada definitiva (solo nombres PET)
PET_OPTIONS = [
    "PET Almacén Badalona",
    "PET Almacén Ibiza",
    "PET T001 Tienda Ibiza",
    "PET T002 Tienda Marbella",
    "PET T004 Tienda Madrid",
]

# Normalización por si quedaron valores antiguos (BAD/IBI/...)
SHORT_TO_PET = {
    "BAD": "PET Almacén Badalona",
    "IBI": "PET Almacén Ibiza",
    "T001": "PET T001 Tienda Ibiza",
    "T002": "PET T002 Tienda Marbella",
    "T004": "PET T004 Tienda Madrid",
}

def normalize_pet(v: str) -> str:
    if v in SHORT_TO_PET:
        return SHORT_TO_PET[v]
    return v if v in PET_OPTIONS else PET_OPTIONS[0]

# Formulario de cabecera
c1, c2, c3, c4 = st.columns([1.2, 1.6, 1.6, 2.0])

with c1:
    st.session_state.fecha = st.date_input("Fecha", value=st.session_state.fecha)

# Aseguramos que session_state ya esté en PET antes de pintar selectbox
st.session_state["origen"] = normalize_pet(st.session_state.get("origen", PET_OPTIONS[0]))
st.session_state["destino"] = normalize_pet(st.session_state.get("destino", PET_OPTIONS[1]))

with c2:
    st.session_state.origen = st.selectbox(
        "Almacén de origen",
        PET_OPTIONS,
        index=PET_OPTIONS.index(st.session_state.origen) if st.session_state.origen in PET_OPTIONS else 0,
    )

with c3:
    st.session_state.destino = st.selectbox(
        "Almacén de destino",
        PET_OPTIONS,
        index=PET_OPTIONS.index(st.session_state.destino) if st.session_state.destino in PET_OPTIONS else 1,
    )

with c4:
    st.session_state.ref_peticion = st.text_input(
        "Referencia de la petición (se exporta en Observaciones)",
        value=st.session_state.ref_peticion,
        placeholder="Ej: PET-2026-02-08-MARBELLA",
    )

# Bloqueo: origen y destino no pueden coincidir
if st.session_state.origen == st.session_state.destino:
    st.warning("Origen y destino no pueden coincidir. Cambia uno de los dos para continuar.")
    st.stop()

st.markdown("<hr/>", unsafe_allow_html=True)

# Plantilla: recomendable (necesaria para exportar)
if st.session_state.get("tpl_bytes") is None:
    st.warning("No se encontró **plantilla_pedido.xlsx** en la raíz del repositorio. Podrás trabajar, pero no exportar.")

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
