# pages/1_Importar_ventas_reposicion.py
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
    "<div class='small'>Sube el Excel de ventas/reposición para precargar el <b>carrito importado</b>. "
    "Si no lo subes, puedes añadir todo manualmente.</div>",
    unsafe_allow_html=True,
)

# Estado mínimo seguro
st.session_state.setdefault("carrito_import", {})
st.session_state.setdefault("pending_rows", [])
st.session_state.setdefault("last_import_stats", None)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

cat = st.session_state.catalog_df
idx_exact, idx_ref_color, idx_ref_talla, idx_ref = build_catalog_indexes(cat)

c1, c2 = st.columns([2.2, 1.0])
with c1:
    petition_file = st.file_uploader(
        "Excel de ventas/reposición",
        type=["xlsx", "xls"],
        key="u_petition",
    )
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
    st.info("No has subido fichero. Este paso es opcional — puedes continuar a **2 · Selección manual**.")
else:
    # Diagnóstico del archivo (siempre visible cuando hay fichero)
    try:
        raw = petition_file.getvalue()
    except Exception:
        # fallback raro, pero por si acaso
        raw = bytes(petition_file.getbuffer())

    st.caption(f"Archivo: **{getattr(petition_file, 'name', '')}** · Bytes recibidos: **{len(raw)}**")

    # Aviso claro si el móvil no está entregando bytes
    if len(raw) < 2000:
        st.warning(
            "El fichero está llegando vacío/incompleto (bytes muy bajos). "
            "En móvil: descárgalo primero a **Archivos/Files** y selecciona el fichero desde ahí (no desde vista previa de WhatsApp/Drive)."
        )

    if st.button("Procesar importación", type="primary"):
        if len(raw) < 2000:
            st.error("No se puede procesar: el fichero no ha llegado correctamente (bytes insuficientes).")
            st.stop()

        # 1) Leer Excel con tu función actual (y mostrar errores reales)
        try:
            pet_df = read_petition_excel(raw)
        except Exception as e:
            st.error("Error leyendo el Excel con `read_petition_excel()`.")
            st.exception(e)
            st.stop()

        # 2) Preview y metadatos para saber si estamos leyendo algo útil
        st.caption(f"Filas leídas: **{len(pet_df)}** · Columnas: **{list(pet_df.columns)}**")
        st.dataframe(pet_df.head(30), use_container_width=True, hide_index=True)

        if pet_df is None or len(pet_df) == 0:
            st.error(
                "El Excel se ha leído pero no se han obtenido filas útiles. "
                "Suele pasar si es una tabla dinámica con cabecera desplazada o si el lector filtra demasiado."
            )
            st.stop()

        # 3) Cruce contra catálogo
        try:
            matched, pending = match_petition_to_catalog(
                pet_df, idx_exact, idx_ref_color, idx_ref_talla, idx_ref
            )
        except Exception as e:
            st.error("Error cruzando ventas con catálogo (`match_petition_to_catalog`).")
            st.exception(e)
            st.stop()

        # 4) Añadir al carrito importado
        try:
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
            st.success("Importación aplicada.")
        except Exception as e:
            st.error("Error añadiendo líneas al carrito importado.")
            st.exception(e)
            st.stop()

# Métricas
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
