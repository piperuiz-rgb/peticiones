# pages/2_Seleccion_manual.py
import re
import streamlit as st
from utils import init_state, ensure_style, load_repo_data, add_to_cart

st.set_page_config(page_title="Selección manual", page_icon="🔎", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 2 · Selección manual")
st.markdown("<div class='small'>Busca por referencia / nombre / EAN y ajusta cantidades con grid Color×Talla (carrito manual).</div>", unsafe_allow_html=True)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

cat = st.session_state.catalog_df

c1, c2, c3 = st.columns([2.2, 1.2, 1.2])
with c1:
    st.session_state.search_query = st.text_input(
        "Buscar (ref / nombre / EAN / color / talla)",
        value=st.session_state.search_query,
        placeholder="Ej: 'sabhy', '248202', 'negro', '8445...'",
    )
with c2:
    show_limit = st.selectbox("Máx resultados", [20, 50, 100, 200], index=1)
with c3:
    if st.button("Vaciar carrito manual", use_container_width=True):
        st.session_state.carrito_manual = {}

q = (st.session_state.search_query or "").strip().lower()
if q:
    mask = st.session_state.search_blob.str.contains(re.escape(q), na=False)
    hits = cat.loc[mask, ["Referencia", "Nombre", "Color", "Talla", "EAN"]].copy()
else:
    hits = cat.loc[:, ["Referencia", "Nombre", "Color", "Talla", "EAN"]].head(0)

hits = hits.drop_duplicates(subset=["Referencia", "Nombre"]).head(show_limit)

ref_options = sorted(hits["Referencia"].dropna().astype(str).unique().tolist())
if ref_options:
    sel_ref = st.selectbox(
        "Selecciona referencia",
        options=[""] + ref_options,
        index=0 if not st.session_state.selected_ref else (ref_options.index(st.session_state.selected_ref) + 1 if st.session_state.selected_ref in ref_options else 0),
    )
    st.session_state.selected_ref = sel_ref or ""
else:
    st.info("Escribe una búsqueda para empezar." if not q else "No hay resultados para esa búsqueda.")

if st.session_state.selected_ref:
    ref = st.session_state.selected_ref
    ref_df = cat[cat["Referencia"] == ref].copy()

    if ref_df.empty:
        st.warning("No se encontraron variantes para esa referencia en catálogo.")
    else:
        nombre = ref_df["Nombre"].iloc[0] if "Nombre" in ref_df.columns else ""
        st.markdown(
            f"<div class='card'><div><span class='badge'>REF</span> "
            f"<span class='mono'>{ref}</span></div>"
            f"<div style='margin-top:6px; font-weight:600;'>{nombre}</div>"
            f"<div class='small' style='margin-top:4px;'>Ajusta cantidades por color y talla. "
            f"Se añaden al <b>carrito manual</b>.</div></div>",
            unsafe_allow_html=True,
        )

        colors = sorted(ref_df["Color"].dropna().astype(str).unique().tolist())
        tallas = sorted(ref_df["Talla"].dropna().astype(str).unique().tolist(), key=lambda x: (len(x), x))

        var_map = {}
        for _, r in ref_df.iterrows():
            var_map[(str(r["Color"]), str(r["Talla"]))] = {
                "EAN": str(r["EAN"]),
                "Referencia": str(r["Referencia"]),
                "Nombre": str(r["Nombre"]),
                "Color": str(r["Color"]),
                "Talla": str(r["Talla"]),
            }

        st.markdown("<div class='gridwrap'>", unsafe_allow_html=True)
        header_cols = st.columns([1.2] + [1.0] * len(colors))
        header_cols[0].markdown("**Talla \\ Color**")
        for j, col in enumerate(colors, start=1):
            header_cols[j].markdown(f"**{col}**")

        for talla in tallas:
            row_cols = st.columns([1.2] + [1.0] * len(colors))
            row_cols[0].markdown(f"**{talla}**")
            for j, col in enumerate(colors, start=1):
                variant = var_map.get((col, talla))
                if not variant:
                    row_cols[j].markdown("<div class='cellqty small'>—</div>", unsafe_allow_html=True)
                    continue

                ean = variant["EAN"]
                current_qty = int(st.session_state.carrito_manual.get(ean, {}).get("Cantidad", 0))

                b1, b2, b3 = row_cols[j].columns([1, 1, 1])
                with b1:
                    if st.button("−", key=f"minus_{ref}_{col}_{talla}", use_container_width=True):
                        add_to_cart(st.session_state.carrito_manual, variant, -1)
                        st.rerun()
                with b2:
                    st.markdown(f"<div class='cellqty'>{current_qty}</div>", unsafe_allow_html=True)
                with b3:
                    if st.button("＋", key=f"plus_{ref}_{col}_{talla}", use_container_width=True):
                        add_to_cart(st.session_state.carrito_manual, variant, +1)
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

from utils import nav_buttons

nav_buttons(
    prev_page="pages/1_Importar_ventas_reposicion.py",
    next_page="pages/3_Revision_final.py",
    next_label="Revisar carritos →"
)
