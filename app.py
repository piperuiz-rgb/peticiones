# app.py
import streamlit as st
import utils

st.set_page_config(page_title="Peticiones almacenes", page_icon="📦", layout="wide")
utils.ensure_style()
utils.init_state()
utils.load_repo_data()

st.markdown("# 0 · Datos del pedido")
st.markdown(
    "<div class='small'>Catálogo y plantilla se cargan automáticamente desde el repositorio.</div>",
    unsafe_allow_html=True,
)

# Catálogo obligatorio
if not st.session_state.get("cat_loaded"):
    st.error("No se encontró **catalogue.xlsx** en la raíz del repositorio.")
    st.stop()

OPTIONS = utils.PET_WAREHOUSES

# Normaliza valores antiguos (BAD/T002…) si existieran en session_state
st.session_state["origen"] = utils.normalize_warehouse(st.session_state.get("origen", OPTIONS[0]))
st.session_state["destino"] = utils.normalize_warehouse(st.session_state.get("destino", OPTIONS[1] if len(OPTIONS) > 1 else OPTIONS[0]))

# Asegura por defecto que no coincidan (evita “me quedo en esta página”)
if st.session_state["origen"] == st.session_state["destino"] and len(OPTIONS) > 1:
    st.session_state["destino"] = OPTIONS[1]

c1, c2, c3, c4 = st.columns([1.2, 1.4, 1.4, 2.0])

with c1:
    st.session_state.fecha = st.date_input("Fecha", value=st.session_state.fecha)

with c2:
    st.session_state.origen = st.selectbox(
        "Almacén de origen",
        OPTIONS,
        index=OPTIONS.index(st.session_state.origen) if st.session_state.origen in OPTIONS else 0,
    )

with c3:
    st.session_state.destino = st.selectbox(
        "Almacén de destino",
        OPTIONS,
        index=OPTIONS.index(st.session_state.destino) if st.session_state.destino in OPTIONS else 1,
    )

with c4:
    st.session_state.ref_peticion = st.text_input(
        "Referencia de la petición (se exporta en Observaciones)",
        value=st.session_state.ref_peticion,
        placeholder="Ej: PET-2026-02-IBIZA",
    )

# Bloqueo: origen = destino
if st.session_state.origen == st.session_state.destino:
    st.warning("El almacén de origen y destino no pueden ser el mismo. Cambia uno de los dos para continuar.")
    st.stop()

st.markdown("<hr/>", unsafe_allow_html=True)

# Aviso plantilla
if st.session_state.get("tpl_bytes") is None:
    st.warning(
        "No se encontró **plantilla_pedido.xlsx** en la raíz del repositorio. "
        "Podrás trabajar, pero no exportar."
    )

st.markdown("### Siguiente paso")
st.page_link("pages/1_Importar_ventas_reposicion.py", label="Continuar a 1 · Importar ventas/reposición →", use_container_width=True)
st.page_link("pages/2_Seleccion_manual.py", label="Saltar importación y pasar a 2 · Selección manual →", use_container_width=True)
