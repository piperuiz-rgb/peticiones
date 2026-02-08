# pages/3_Revision_final.py
import streamlit as st
from utils import init_state, ensure_style, load_repo_data, merge_carts

st.set_page_config(page_title="Revisión", page_icon="🧾", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 3 · Revisión final")
st.markdown(
    "<div class='small'>Revisa el pedido final agrupado por referencia y ajusta cantidades antes de exportar.</div>",
    unsafe_allow_html=True,
)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

def set_qty_in_base_carts(ean: str, new_qty: int):
    """
    Mantiene la compatibilidad con tu modelo actual (2 carritos por debajo),
    pero el usuario ve 1 revisión fusionada.
    """
    new_qty = int(new_qty)

    if new_qty <= 0:
        st.session_state.carrito_import.pop(ean, None)
        st.session_state.carrito_manual.pop(ean, None)
        return

    if ean in st.session_state.carrito_import:
        st.session_state.carrito_import[ean]["Cantidad"] = new_qty
        return

    if ean in st.session_state.carrito_manual:
        st.session_state.carrito_manual[ean]["Cantidad"] = new_qty
        return

    # Fallback improbable: si no está en ninguno, lo metemos en manual
    # (esto evita inconsistencias en caso de estados raros)
    st.session_state.carrito_manual[ean] = {
        "EAN": ean,
        "Ref": "",
        "Nom": "",
        "Col": "",
        "Tal": "",
        "Cantidad": new_qty,
    }

merged = merge_carts(st.session_state.carrito_import, st.session_state.carrito_manual)

if not merged:
    st.info("No hay prendas en la petición todavía.")
    st.page_link("pages/2_Seleccion_manual.py", label="← Volver a selección manual", use_container_width=True)
    st.stop()

# -----------------------------
# Totales
# -----------------------------
total_lines = len(merged)
total_units = sum(int(v.get("Cantidad", 0)) for v in merged.values())
total_refs = len(set(v.get("Ref", "") for v in merged.values() if v.get("Ref", "")))

m1, m2, m3 = st.columns(3)
m1.metric("Referencias", total_refs)
m2.metric("Líneas", total_lines)
m3.metric("Unidades", total_units)

st.markdown("<hr/>", unsafe_allow_html=True)

# -----------------------------
# Agrupar por referencia
# -----------------------------
groups = {}
for ean, it in merged.items():
    ref = it.get("Ref", "") or "-"
    groups.setdefault(ref, []).append((ean, it))

# Orden por referencia
for ref in sorted(groups.keys()):
    items = groups[ref]
    # nombre “principal” (si hay)
    name = next((it.get("Nom", "") for _, it in items if it.get("Nom")), "")
    units_ref = sum(int(it.get("Cantidad", 0)) for _, it in items)
    lines_ref = len(items)

    title = f"{ref} · {lines_ref} líneas · {units_ref} uds"
    with st.expander(title, expanded=True):
        if name:
            st.markdown(f"<div class='small'>{name}</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        header = st.columns([3.8, 1.0, 0.6, 0.6])
        header[0].markdown("**Variante**")
        header[1].markdown("**Qty**")
        header[2].markdown("")
        header[3].markdown("")

        # Orden por color/talla para lectura
        items_sorted = sorted(items, key=lambda x: (x[1].get("Col", ""), x[1].get("Tal", "")))

        for ean, it in items_sorted:
            col = it.get("Col", "-")
            tal = it.get("Tal", "-")
            qty = int(it.get("Cantidad", 0))

            row = st.columns([3.8, 1.0, 0.6, 0.6])

            with row[0]:
                st.markdown(
                    f"<span class='mono'>{col}</span> / <span class='mono'>{tal}</span><br>"
                    f"<span class='small'>EAN {ean}</span>",
                    unsafe_allow_html=True,
                )

            with row[1]:
                st.markdown(f"<div class='cellqty'>{qty}</div>", unsafe_allow_html=True)

            with row[2]:
                if st.button("−", key=f"rev_minus_{ean}", use_container_width=True):
                    set_qty_in_base_carts(ean, qty - 1)
                    st.rerun()

            with row[3]:
                if st.button("＋", key=f"rev_plus_{ean}", use_container_width=True):
                    set_qty_in_base_carts(ean, qty + 1)
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr/>", unsafe_allow_html=True)
st.page_link("pages/4_Exportar.py", label="Confirmar y exportar →", use_container_width=True)
st.page_link("pages/2_Seleccion_manual.py", label="← Volver a selección manual", use_container_width=True)
