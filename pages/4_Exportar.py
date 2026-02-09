# pages/4_Exportar.py
import io
import re
import streamlit as st
from openpyxl import load_workbook
from utils import init_state, ensure_style, load_repo_data, merge_carts

st.set_page_config(page_title="Exportar", page_icon="📦", layout="wide")
ensure_style()
init_state()
load_repo_data()

st.markdown("# 4 · Exportar pedido")
st.markdown("<div class='small'>Exportación estricta: si no encuentra la zona de la plantilla, no escribe (para no romper formato).</div>", unsafe_allow_html=True)

merged = merge_carts(st.session_state.get("carrito_import", {}), st.session_state.get("carrito_manual", {}))
if not merged:
    st.warning("No hay líneas en el pedido.")
    st.page_link("pages/3_Revision_final.py", label="← Volver a 3 · Revisión", use_container_width=True)
    st.stop()

tpl = st.session_state.get("tpl_bytes")
if tpl is None:
    st.error("No se encontró `plantilla_pedido.xlsx` en el repositorio.")
    st.stop()

origen = st.session_state.get("origen", "")
destino = st.session_state.get("destino", "")
ref_txt = st.session_state.get("ref_peticion", "") or ""

if origen == destino:
    st.error("Origen y destino no pueden coincidir.")
    st.stop()

def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", (s or "").strip())

def find_cell_containing(ws, needle: str, max_rows=120, max_cols=60):
    needle = needle.strip().lower()
    for r in range(1, min(ws.max_row, max_rows) + 1):
        for c in range(1, min(ws.max_column, max_cols) + 1):
            v = ws.cell(r, c).value
            if isinstance(v, str) and v.strip().lower() == needle:
                return (r, c)
    return None

def find_header_row(ws, headers, max_rows=160, max_cols=80):
    want = [h.lower() for h in headers]
    for r in range(1, min(ws.max_row, max_rows) + 1):
        colmap = {}
        for c in range(1, min(ws.max_column, max_cols) + 1):
            v = ws.cell(r, c).value
            if isinstance(v, str):
                colmap[v.strip().lower()] = c
        hits = sum(1 for h in want if h in colmap)
        if hits >= len(want):  # estricto: deben estar TODOS
            return r, colmap
    return None, None

# Cargar plantilla
wb = load_workbook(io.BytesIO(tpl))
ws = wb.active

# 1) Cabecera: exige que existan etiquetas en plantilla (evita escribir en B2/B3 a ciegas)
pos_origen = find_cell_containing(ws, "origen")
pos_destino = find_cell_containing(ws, "destino")
pos_obs = find_cell_containing(ws, "observaciones")

missing = []
if not pos_origen: missing.append("Origen")
if not pos_destino: missing.append("Destino")
if not pos_obs: missing.append("Observaciones")

if missing:
    st.error(
        "La plantilla no contiene las etiquetas esperadas para cabecera: "
        + ", ".join(missing)
        + ".\n\nSolución: en la plantilla debe existir literalmente una celda con 'Origen', otra con 'Destino' y otra con 'Observaciones'."
    )
    st.stop()

# Escribimos en la celda de la derecha (col+1)
ws.cell(pos_origen[0], pos_origen[1] + 1).value = origen
ws.cell(pos_destino[0], pos_destino[1] + 1).value = destino
ws.cell(pos_obs[0], pos_obs[1] + 1).value = ref_txt

# 2) Tabla líneas: exige cabeceras exactas para no romper formato
# Ajusta estos nombres EXACTOS a los que tenga tu plantilla en la fila cabecera:
REQUIRED_HEADERS = ["EAN", "Cantidad"]
header_row, colmap = find_header_row(ws, REQUIRED_HEADERS)

if not header_row:
    st.error(
        "No encuentro una fila de cabecera con las columnas EXACTAS: "
        f"{REQUIRED_HEADERS}. "
        "Para no desconfigurar la plantilla, la exportación se detiene."
    )
    st.stop()

# Columnas (puedes ampliar si tu plantilla tiene más)
col_ean = colmap["ean"]
col_qty = colmap["cantidad"]

# Opcionales si existen en plantilla
col_ref = colmap.get("ref") or colmap.get("referencia")
col_nombre = colmap.get("nombre") or colmap.get("producto")
col_color = colmap.get("color")
col_talla = colmap.get("talla")
col_obs = colmap.get("observaciones")

start_row = header_row + 1

# No limpiamos a lo bestia; solo escribimos tantas filas como necesitemos
rows = []
for ean, it in merged.items():
    qty = int(it.get("Cantidad", 0) or 0)
    if qty <= 0:
        continue
    rows.append(
        {
            "EAN": str(ean),
            "Ref": it.get("Ref", ""),
            "Nombre": it.get("Nom", ""),
            "Color": it.get("Col", ""),
            "Talla": it.get("Tal", ""),
            "Cantidad": qty,
            "Observaciones": ref_txt,
        }
    )

rows.sort(key=lambda x: (x["Ref"], x["Color"], x["Talla"], x["EAN"]))

for i, item in enumerate(rows):
    r = start_row + i
    ws.cell(r, col_ean).value = item["EAN"]
    ws.cell(r, col_qty).value = item["Cantidad"]

    if col_ref: ws.cell(r, col_ref).value = item["Ref"]
    if col_nombre: ws.cell(r, col_nombre).value = item["Nombre"]
    if col_color: ws.cell(r, col_color).value = item["Color"]
    if col_talla: ws.cell(r, col_talla).value = item["Talla"]
    if col_obs: ws.cell(r, col_obs).value = item["Observaciones"]

# Guardar
safe_ref = _safe(ref_txt) if ref_txt else "SIN_REF"
filename = f"{st.session_state.get('fecha'):%Y%m%d}_{safe_ref}.xlsx".replace(" ", "_")

out = io.BytesIO()
wb.save(out)
out.seek(0)

st.success("Exportación lista.")
st.download_button(
    "Descargar Excel",
    data=out.getvalue(),
    file_name=filename,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.page_link("pages/3_Revision_final.py", label="← Volver a 3 · Revisión", use_container_width=True)
