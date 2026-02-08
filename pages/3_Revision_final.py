# pages/3_Revision_final.py
import re
import streamlit as st
from utils import init_state, ensure_style, load_repo_data, merge_carts

st.set_page_config(page_title="Revisión", page_icon="🧾", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 3 · Revisión final")
st.markdown(
    "<div class='small'>Filtra por referencia/nombre y ajusta cantidades antes de exportar.</div>",
    unsafe_allow_html=True,
)

if not st.session_state.get("cat_loaded"):
    st.error("No se encontró `catalogue.xlsx` en la raíz del repositorio.")
    st.stop()

# Estado UI
st.session_state.setdefault("rev_expand_all", True)
st.session_state.setdefault("rev_filter", "")

def set_qty_in_base_carts(ean: str, new_qty: int):
    new_qty = int(new_qty)
    if new_qty <= 0:
        st.session_state.carrito_import.pop(ean, None)
        st.session_state.carrito_manual.pop(ean, None)
        return

    if ean in st.session_state.carrito_import:
        st.session_state.carrito_import[ean]["Cantidad"] = new_qty
    elif ean in st.session_state.carrito_manual:
        st.session_state.carrito_manual[ean]["Cantidad"] = new_qty
    else:
        # fallback raro
        st.session_state.carrito_manual[ean] = {
            "EAN": ean, "Ref": "", "Nom": "", "Col": "", "Tal": "", "Cantidad": new_qty
        }

def delete_ref_in_base_carts(ref: str):
    # borra en ambos carritos todas las líneas de esa referencia
    for cart_key in ("carrito_import", "carrito_manual"):
        cart = st.session_state.get(cart_key, {})
        to_del = [ean for ean, it in cart.items() if (it.get("Ref") or "") == ref]
        for ean in to_del:
            cart.pop(ean, None)

merged = merge_carts(st.session_state.carrito_import, st.session_state.carrito_manual)

if not merged:
    st.info("No hay prendas en la petición todavía.")
    st.page_link("pages/2_Seleccion_manual.py", label="← Volver a selección manual", use_container_width=True)
    st.stop()

# -----------------------------
# Barra de herramientas (filtro + expand/collapse)
# -----------------------------
t1, t2, t3 = st.columns([2.2, 1.0, 1.0])
with t1:
    st.session_state.rev_filter = st.text_input(
        "Buscar en revisión",
        value=st.session_state.rev_filter,
        placeholder="Ref, nombre, color, talla, EAN…",
    )
with t2:
    if st.button("Expandir todo", use_container_width=True):
        st.session_state.rev_expand_all = True
        st.rerun()
with t3:
    if st.button("Colapsar todo", use_container_width=True):
        st.session_state.rev_expand_all = False
        st.rerun()

q = (st.session_state.rev_filter or "").strip().lower()

# -----------------------------
# Totales (del pedido completo, no del filtro)
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

def group_matches(ref: str, items):
    if not q:
        return True
    # match por ref, nombre, y cualquier variante
    hay = []
    hay.append(ref)
    for ean, it in items:
        hay.append(it.get("Nom", ""))
        hay.append(it.get("Col", ""))
        hay.append(it.get("Tal", ""))
        hay.append(str(ean))
    blob = " ".join(hay).lower()
    return bool(re.search(re.escape(q), blob))

shown_any = False

for ref in sorted(groups.keys()):
    items = groups[ref]

    if not group_matches(ref, items):
        continue
    shown_any = True

    name = next((it.get("Nom", "") for _, it in items if it.get("Nom")), "")
    units_ref = sum(int(it.get("Cantidad", 0)) for _, it in items)
    lines_ref = len(items)

    # si hay filtro, expandimos por defecto para acelerar revisión
    expanded = True if q else bool(st.session_state.rev_expand_all)

    title = f"{ref} · {lines_ref} líneas · {units_ref} uds"
    with st.expander(title, expanded=expanded):
        top = st.columns([3.0, 1.2])
        with top[0]:
            if name:
                st.markdown(f"<div class='small'>{name}</div>", unsafe_allow_html=True)
        with top[1]:
            if st.button("Eliminar referencia", key=f"delref_{ref}", use_container_width=True):
                delete_ref_in_base_carts(ref)
                st.rerun()

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        header = st.columns([3.8, 1.0, 0.6, 0.6])
        header[0].markdown("**Variante**")
        header[1].markdown("**Qty**")
        header[2].markdown("")
        header[3].markdown("")

        items_sorted = sorted(items, key=lambda x: (x[1].get("Col", ""), x[1].get("Tal", "")))

        for ean, it in items_sorted:
            col = it.get("Col", "-")
            tal = it.get("Tal", "-")
            qty = int(it.get("Cantidad", 0))

            # si hay filtro, también filtramos a nivel variante
            if q:
                vblob = f"{ref} {it.get('Nom','')} {col} {tal} {ean}".lower()
                if q not in vblob:
                    continue

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

if not shown_any:
    st.info("No hay resultados para ese filtro.")

st.markdown("<hr/>", unsafe_allow_html=True)
st.page_link("pages/4_Exportar.py", label="Confirmar y exportar →", use_container_width=True)
st.page_link("pages/2_Seleccion_manual.py", label="← Volver a selección manual", use_container_width=True)
