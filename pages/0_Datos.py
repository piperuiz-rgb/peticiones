# pages/0_Datos.py
import streamlit as st
from utils import init_state, ensure_style, load_repo_data

st.set_page_config(page_title="Datos", page_icon="🗂️", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 0 · Estado de datos")
st.markdown("<div class='small'>Aquí solo validamos que el repositorio tenga los ficheros base.</div>", unsafe_allow_html=True)

ok_cat = st.session_state.get("cat_loaded")
ok_tpl = st.session_state.get("tpl_bytes") is not None

c1, c2 = st.columns(2)
with c1:
    st.markdown("### Catálogo")
    st.write("✅ Cargado desde repo (`catalogue.xlsx`)" if ok_cat else "❌ No encontrado / formato incorrecto (`catalogue.xlsx`)")
with c2:
    st.markdown("### Plantilla")
    st.write("✅ Encontrada (`plantilla_pedido.xlsx`)" if ok_tpl else "⚠️ No encontrada (`plantilla_pedido.xlsx`) — no podrás exportar")

st.markdown("<hr/>", unsafe_allow_html=True)
st.info("El fichero de **ventas/reposición** se sube en la página **1 · Importar** (es opcional).")
