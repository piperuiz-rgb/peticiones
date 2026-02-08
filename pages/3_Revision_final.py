# pages/3_Revision_final.py
import streamlit as st
from utils import init_state, ensure_style, load_repo_data, cart_to_df, merge_carts

st.set_page_config(page_title="Revisión", page_icon="🧾", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 3 · Revisión final")
st.markdown("<div class='small'>Revisa el carrito importado y el manual por separado. La fusión es lo que se exporta.</div>", unsafe_allow_html=True)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

car_imp_df = cart_to_df(st.session_state.carrito_import)
car_man_df = cart_to_df(st.session_state.carrito_manual)
car_merge = merge_carts(st.session_state.carrito_import, st.session_state.carrito_manual)

car_merge_df = cart_to_df(car_merge)[["EAN", "Ref", "Nom", "Col", "Tal", "Cantidad"]].rename(
    columns={"Ref": "Referencia", "Nom": "Nombre", "Col": "Color", "Tal": "Talla"}
)

def apply_edited_cart(edited):
    new_cart = {}
    for _, r in edited.iterrows():
        ean = str(r["EAN"])
        qty = int(r["Cantidad"])
        if qty > 0:
            new_cart[ean] = {
                "EAN": ean,
                "Ref": str(r["Referencia"]),
                "Nom": str(r["Nombre"]),
                "Col": str(r["Color"]),
                "Tal": str(r["Talla"]),
                "Cantidad": qty,
            }
    return new_cart

cA, cB, cC = st.columns(3)

with cA:
    st.markdown("<div class='card'><b>Carrito importado</b></div>", unsafe_allow_html=True)
    st.caption(f"{len(car_imp_df)} líneas")
    if car_imp_df.empty:
        st.info("Vacío.")
    else:
        edit_df = car_imp_df.rename(columns={"Ref": "Referencia", "Nom": "Nombre", "Col": "Color", "Tal": "Talla"})
        edited = st.data_editor(edit_df, use_container_width=True, hide_index=True,
                                disabled=["EAN","Referencia","Nombre","Color","Talla"])
        st.session_state.carrito_import = apply_edited_cart(edited)

with cB:
    st.markdown("<div class='card'><b>Carrito manual</b></div>", unsafe_allow_html=True)
    st.caption(f"{len(car_man_df)} líneas")
    if car_man_df.empty:
        st.info("Vacío.")
    else:
        edit_df = car_man_df.rename(columns={"Ref": "Referencia", "Nom": "Nombre", "Col": "Color", "Tal": "Talla"})
        edited = st.data_editor(edit_df, use_container_width=True, hide_index=True,
                                disabled=["EAN","Referencia","Nombre","Color","Talla"])
        st.session_state.carrito_manual = apply_edited_cart(edited)

with cC:
    st.markdown("<div class='card'><b>Fusión (se exporta)</b></div>", unsafe_allow_html=True)
    st.caption(f"{len(car_merge_df)} líneas")
    if car_merge_df.empty:
        st.info("No hay líneas para exportar.")
    else:
        st.dataframe(car_merge_df, use_container_width=True, hide_index=True)
