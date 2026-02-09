# pages/2_Seleccion_manual.py
import re
import streamlit as st
import pandas as pd
from utils import init_state, ensure_style, load_repo_data, add_to_cart

st.set_page_config(page_title="Selección manual", page_icon="🔎", layout="wide")
ensure_style()
init_state()
load_repo_data()

# CSS: JOOR-ish (limpio, tabular, jerarquía visual)
st.markdown(
    """
<style>
/* Tipografía / jerarquía */
.joor-kicker { font-size: 12px; opacity: .75; letter-spacing: .06em; text-transform: uppercase; }
.joor-title  { font-size: 18px; font-weight: 800; margin-top: 2px; }
.joor-sub    { font-size: 13px; opacity: .75; }

/* Chips */
.joor-chip {
  display: inline-block;
  padding: 3px 8px;
  border: 1px solid #eee;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: #fafafa;
}

/* Grid header tipo tabla + sticky */
.grid-header-row {
  background: #fafafa;
  border: 1px solid #eee;
  padding: 8px 8px;
  border-radius: 10px;
  margin-bottom: 8px;

  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 6px 14px rgba(0,0,0,0.04);
}

.grid-hdr {
  text-align: center;
  font-weight: 800;
  white-space: nowrap;
  min-width: 120px;
}

.grid-hdr-left {
  font-weight: 800;
  white-space: nowrap;
}

.grid-colcell {
  border-left: 1px solid #eee;
  padding-left: 8px;
  min-width: 120px;
}

.grid-rowlabel {
  font-weight: 800;
  white-space: nowrap;
  padding-top: 10px;
}

.grid-colcell button[kind="secondary"] {
  font-size: 18px;
  font-weight: 800;
}

/* Panel carrito */
.cartpanel {
  border: 1px solid #eee;
  background: #fff;
  border-radius: 14px;
  padding: 10px 10px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("# 2 · Selección manual")
st.markdown(
    "<div class='joor-sub'>Busca por referencia / nombre / EAN y ajusta cantidades en el grid Color×Talla. "
    "Se añade al <b>carrito manual</b>.</div>",
    unsafe_allow_html=True,
)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

cat = st.session_state.catalog_df

# -----------------------------
# Layout 2 columnas (JOOR-ish)
# -----------------------------
left, right = st.columns([1.05, 1.95], gap="large")

with left:
    st.markdown("<div class='joor-kicker'>Browse</div>", unsafe_allow_html=True)
    st.markdown("<div class='joor-title'>Buscar producto</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        st.session_state.search_query = st.text_input(
            "Buscar (ref / nombre / EAN / color / talla)",
            value=st.session_state.search_query,
            placeholder="Ej: 248202 · sabhy · negro · 8445…",
            label_visibility="visible",
        )
    with c2:
        show_limit = st.selectbox("Máx", [20, 50, 100, 200], index=1)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("Vaciar carrito manual", use_container_width=True):
            st.session_state.carrito_manual = {}
    with b2:
        if st.button("Limpiar búsqueda", use_container_width=True):
            st.session_state.search_query = ""
            st.session_state.selected_ref = ""
            st.rerun()

    q = (st.session_state.search_query or "").strip().lower()
    if q:
        mask = st.session_state.search_blob.str.contains(re.escape(q), na=False)
        hits = cat.loc[mask, ["Referencia", "Nombre", "Color", "Talla", "EAN"]].copy()
    else:
        hits = cat.loc[:, ["Referencia", "Nombre", "Color", "Talla", "EAN"]].head(0)

    # Deduplicamos por referencia+nombre para selector
    hits2 = hits.drop_duplicates(subset=["Referencia", "Nombre"]).head(show_limit).copy()

    # Mapa ref -> nombre para mostrar en selector
    ref_name = {}
    for _, r in hits2.iterrows():
        ref = str(r.get("Referencia", "") or "")
        nom = str(r.get("Nombre", "") or "")
        if ref and ref not in ref_name:
            ref_name[ref] = nom

    ref_options = sorted(ref_name.keys())

    if not q:
        st.info("Escribe una búsqueda para ver resultados.")
    elif not ref_options:
        st.warning("No hay resultados para esa búsqueda.")

    # Selector: muestra "REF — Nombre"
    if ref_options:
        def fmt_ref(r: str) -> str:
            nom = (ref_name.get(r) or "").strip()
            return f"{r} — {nom}" if nom else r

        # index actual si existe
        idx = 0
        if st.session_state.get("selected_ref") in ref_options:
            idx = ref_options.index(st.session_state.selected_ref)

        sel_ref = st.selectbox(
            "Resultados",
            options=ref_options,
            index=idx,
            format_func=fmt_ref,
        )
        st.session_state.selected_ref = sel_ref

        # Vista rápida opcional (ref + nombre)
        with st.expander("Ver lista", expanded=False):
            df_list = pd.DataFrame(
                [{"Referencia": r, "Nombre": ref_name.get(r, "")} for r in ref_options]
            )
            st.dataframe(df_list, use_container_width=True, hide_index=True)

with right:
    st.markdown("<div class='joor-kicker'>Product grid</div>", unsafe_allow_html=True)
    if st.session_state.get("selected_ref"):
        ref = st.session_state.selected_ref
        ref_df = cat[cat["Referencia"] == ref].copy()

        if ref_df.empty:
            st.warning("No se encontraron variantes para esa referencia en catálogo.")
            st.stop()

        nombre = ref_df["Nombre"].iloc[0] if "Nombre" in ref_df.columns else ""
        st.markdown(
            f"<div class='card'>"
            f"<div style='display:flex; gap:8px; align-items:center;'>"
            f"<span class='joor-chip'>REF</span><span class='mono' style='font-weight:800'>{ref}</span>"
            f"</div>"
            f"<div style='margin-top:6px; font-weight:800; font-size:16px;'>{nombre}</div>"
            f"<div class='joor-sub' style='margin-top:4px;'>Ajusta cantidades por color y talla.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        colors = sorted(ref_df["Color"].dropna().astype(str).unique().tolist())
        tallas = sorted(ref_df["Talla"].dropna().astype(str).unique().tolist(), key=lambda x: (len(x), x))

        # Mapa de variantes
        var_map = {}
        for _, r in ref_df.iterrows():
            var_map[(str(r["Color"]), str(r["Talla"]))] = {
                "EAN": str(r["EAN"]),
                "Referencia": str(r["Referencia"]),
                "Nombre": str(r["Nombre"]),
                "Color": str(r["Color"]),
                "Talla": str(r["Talla"]),
            }

        # Cabecera sticky (por CSS)
        header_cols = st.columns([1.2] + [1.0] * len(colors))
        header_cols[0].markdown("<div class='grid-header-row grid-hdr-left'>Talla \\ Color</div>", unsafe_allow_html=True)
        for j, col in enumerate(colors, start=1):
            header_cols[j].markdown(f"<div class='grid-header-row grid-hdr'>{col}</div>", unsafe_allow_html=True)

        # Filas por talla
        for talla in tallas:
            row_cols = st.columns([1.2] + [1.0] * len(colors))
            row_cols[0].markdown(f"<div class='grid-rowlabel'>{talla}</div>", unsafe_allow_html=True)

            for j, col in enumerate(colors, start=1):
                variant = var_map.get((col, talla))

                if not variant:
                    row_cols[j].markdown(
                        "<div class='grid-colcell'><div class='cellqty small'>—</div></div>",
                        unsafe_allow_html=True,
                    )
                    continue

                ean = variant["EAN"]
                current_qty = int(st.session_state.carrito_manual.get(ean, {}).get("Cantidad", 0))

                row_cols[j].markdown("<div class='grid-colcell'>", unsafe_allow_html=True)

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

                row_cols[j].markdown("</div>", unsafe_allow_html=True)

    else:
        st.info("Selecciona una referencia desde la izquierda para ver el grid.")

# -----------------------------
# Panel: Carrito manual (en la misma página)
# -----------------------------
st.markdown("<hr/>", unsafe_allow_html=True)

carrito = st.session_state.get("carrito_manual", {}) or {}
total_lines = len(carrito)
total_units = sum(int(v.get("Cantidad", 0)) for v in carrito.values())

with st.expander(f"Carrito manual · {total_lines} líneas · {total_units} uds", expanded=True):
    st.markdown("<div class='cartpanel'>", unsafe_allow_html=True)

    if not carrito:
        st.info("Aún no has añadido prendas al carrito manual.")
    else:
        selected_ref = st.session_state.get("selected_ref", "")
        show_only_ref = st.checkbox(
            "Mostrar solo la referencia seleccionada",
            value=bool(selected_ref),
            disabled=not bool(selected_ref),
        )

        items = []
        for ean, it in carrito.items():
            if show_only_ref and selected_ref and it.get("Ref") != selected_ref:
                continue
            items.append((ean, it))

        if not items:
            st.info("No hay líneas del carrito manual para esa referencia.")
        else:
            h = st.columns([2.4, 1.2, 1.0, 0.6, 0.6, 0.6])
            h[0].markdown("**Ref / Producto**")
            h[1].markdown("**Color / Talla**")
            h[2].markdown("**Qty**")
            h[3].markdown("")
            h[4].markdown("")
            h[5].markdown("")

            items_sorted = sorted(items, key=lambda x: (x[1].get("Ref", ""), x[1].get("Col", ""), x[1].get("Tal", "")))

            for ean, it in items_sorted:
                ref = it.get("Ref", "")
                nom = it.get("Nom", "")
                col = it.get("Col", "-")
                tal = it.get("Tal", "-")
                qty = int(it.get("Cantidad", 0))

                row = st.columns([2.4, 1.2, 1.0, 0.6, 0.6, 0.6])

                with row[0]:
                    st.markdown(f"**{ref}**<br><span class='small'>{nom}</span>", unsafe_allow_html=True)
                with row[1]:
                    st.markdown(f"<span class='mono'>{col}</span> / <span class='mono'>{tal}</span>", unsafe_allow_html=True)
                with row[2]:
                    st.markdown(f"<div class='cellqty'>{qty}</div>", unsafe_allow_html=True)

                variant = {"EAN": ean, "Referencia": ref, "Nombre": nom, "Color": col, "Talla": tal}

                with row[3]:
                    if st.button("−", key=f"cart_minus_{ean}", use_container_width=True):
                        add_to_cart(st.session_state.carrito_manual, variant, -1)
                        st.rerun()
                with row[4]:
                    if st.button("＋", key=f"cart_plus_{ean}", use_container_width=True):
                        add_to_cart(st.session_state.carrito_manual, variant, +1)
                        st.rerun()
                with row[5]:
                    if st.button("🗑️", key=f"cart_del_{ean}", use_container_width=True):
                        st.session_state.carrito_manual.pop(ean, None)
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

st.page_link("pages/3_Revision_final.py", label="Continuar a 3 · Revisión final →", use_container_width=True)
st.page_link("pages/1_Importar_ventas_reposicion.py", label="← Volver a 1 · Importar", use_container_width=True)
