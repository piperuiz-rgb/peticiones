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

merged = merge_carts(st.session_state.get("carrito_import", {}), st.session_state.get("carrito_manual", {}))
if not merged:
    st.warning("No hay líneas en el pedido.")
    st.page_link("pages/3_Revision_final.py", label="← Volver a 3 · Revisión", use_container_width=True)
    st.stop()

tpl = st.session_state.get("tpl_bytes")
if tpl is None:
    st.error("No se encontró `plantilla_pedido.xlsx` en el repositorio.")
    st.stop()

# Aquí deben ser PET (si en algún lado quedó BAD, lo convertimos)
SHORT_TO_PET = {
    "BAD": "PET Almacén Badalona",
    "IBI": "PET Almacén Ibiza",
    "T001": "PET T001 Tienda Ibiza",
    "T002": "PET T002 Tienda Marbella",
    "T004": "PET T004 Tienda Madrid",
}
origen = SHORT_TO_PET.get(st.session_state.get("origen", ""), st.session_state.get("origen", ""))
destino = SHORT_TO_PET.get(st.session_state.get("destino", ""), st.session_state.get("destino", ""))
obs = st.session_state.get("ref_peticion", "") or ""
fecha = st.session_state.get("fecha")

if origen == destino:
    st.error("Origen y destino no pueden coincidir.")
    st.stop()

def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", (s or "").strip())

# Cargar plantilla
wb = load_workbook(io.BytesIO(tpl))
ws = wb.active

# Validación plantilla EXACTA (no tocamos nada si no coincide)
expected = ["Fecha", "Almacén de origen", "Almacén de destino", "Observaciones", "EAN", "Cantidad"]
row1 = [ws.cell(1, c).value for c in range(1, 7)]
if [str(x).strip() if x is not None else "" for x in row1] != expected:
    st.error(
        "La plantilla no coincide con la estructura esperada.\n\n"
        f"Esperado en A1–F1: {expected}\n"
        f"Encontrado en A1–F1: {row1}"
    )
    st.stop()

# Construir filas (cada línea = una fila en Excel)
rows = []
for ean, it in merged.items():
    qty = int(it.get("Cantidad", 0) or 0)
    if qty <= 0:
        continue
    rows.append((str(ean), qty, it.get("Ref", ""), it.get("Col", ""), it.get("Tal", "")))

# Orden estable
rows.sort(key=lambda x: (x[2], x[3], x[4], x[0]))

# Limpiar filas antiguas SOLO en el rango usado (no desconfigura estilos del header)
# Borramos contenido de filas 2..(2+len(rows)+50) en columnas A..F
max_clear = max(2 + len(rows) + 50, 60)
for r in range(2, max_clear + 1):
    for c in range(1, 7):
        ws.cell(r, c).value = None

# Escribir
r = 2
for ean, qty, *_ in rows:
    ws.cell(r, 1).value = fecha
    ws.cell(r, 2).value = origen
    ws.cell(r, 3).value = destino
    ws.cell(r, 4).value = obs
    ws.cell(r, 5).value = ean
    ws.cell(r, 6).value = qty
    r += 1

filename = f"{fecha:%Y%m%d}_{_safe(obs) if obs else 'SIN_REF'}.xlsx".replace(" ", "_")

out = io.BytesIO()
wb.save(out)
out.seek(0)

st.success("Archivo listo para descargar.")
st.download_button(
    "Descargar Excel",
    data=out.getvalue(),
    file_name=filename,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

st.page_link("pages/3_Revision_final.py", label="← Volver a 3 · Revisión", use_container_width=True)
