# pages/3_Revision_final.py
import streamlit as st
from utils import (
    init_state,
    ensure_style,
    load_repo_data,
    merge_carts,
)

st.set_page_config(page_title="Revisión", page_icon="🧾", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 3 · Revisión final")
st.markdown(
    "<div class='small'>Revisa y ajusta las cantidades finales antes de exportar.</div>",
    unsafe_allow_html=True,
)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

# Fusión de carritos (estado único para revisión)
merged = merge_carts(
    st.session_state.carrito_import,
    st.session_state.carrito_manual,
)

if not merged:
    st.info("No hay prendas en la petición todavía.")
    st.page_link("pages/2_Seleccion_manual.py", label="← Volver a selección manual", use_container_width=True)
    st.stop()

st.markdown("<div class='card'>", unsafe_allow_html=True)

header = st.columns([3.5, 1.2, 0.6, 0.6])
header[0].markdown("**Prenda**")
header[1].markdown("**Cantidad**")
header[2].markdown("")
header[3].markdown("")

for ean, item in list(merged.items()):
    row = st.columns([3.5, 1.2, 0.6, 0.6])

    with row[0]:
        st.markdown(
            f"<strong>{item['Ref']}</strong><br>"
            f"<span class='small'>{item['Nom']} ({item['Col']} / {item['Tal']})</span>",
            unsafe_allow_html=True,
        )

    with row[1]:
        st.markdown(f"<div class='cellqty'>{item['Cantidad']}</div>", unsafe_allow_html=True)

    with row[2]:
        if st.button("−", key=f"rev_minus_{ean}", use_container_width=True):
            item["Cantidad"] -= 1
            if item["Cantidad"] <= 0:
                st.session_state.carrito_import.pop(ean, None)
                st.session_state.carrito_manual.pop(ean, None)
            else:
                # reflejar en uno de los carritos base
                if ean in st.session_state.carrito_import:
                    st.session_state.carrito_import[ean]["Cantidad"] = item["Cantidad"]
                elif ean in st.session_state.carrito_manual:
                    st.session_state.carrito_manual[ean]["Cantidad"] = item["Cantidad"]
            st.rerun()

    with row[3]:
        if st.button("＋", key=f"rev_plus_{ean}", use_container_width=True):
            item["Cantidad"] += 1
            if ean in st.session_state.carrito_import:
                st.session_state.carrito_import[ean]["Cantidad"] = item["Cantidad"]
            elif ean in st.session_state.carrito_manual:
                st.session_state.carrito_manual[ean]["Cantidad"] = item["Cantidad"]
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)
st.page_link("pages/4_Exportar.py", label="Confirmar y exportar →", use_container_width=True)
st.page_link("pages/2_Seleccion_manual.py", label="← Volver a selección manual", use_container_width=True)
