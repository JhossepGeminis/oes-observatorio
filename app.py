"""
app.py — Observatorio de Educación Superior (OES)
Prototipo académico — Práctica Guiada N.° 08
Tecnologías: Python 3.11+, SQLite, Streamlit, Pandas

Requisitos cubiertos:
  RF01 · Registrar noticia (formulario con todos los campos requeridos)
  RF02 · Filtrar por categoría y texto libre
  RF03 · Calcular indicadores (noticias, instituciones, categorías, fechas)
  RF04 · Exportar resultados a CSV
  RNF01 · Trazabilidad: URL, fecha y fuente siempre visibles
  RNF02 · Funcionamiento 100 % local, sin servicios de pago
"""

import sqlite3
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

# ── Configuración general ────────────────────────────────────────────────────
DB = Path(__file__).with_name("oes.db")

st.set_page_config(
    page_title="OES — Observatorio de Educación Superior",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado suave ──────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Header principal */
    .oes-header {
        background: linear-gradient(135deg, #1a3c5e 0%, #2d6a9f 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        color: white;
    }
    .oes-header h1 { margin: 0; font-size: 1.7rem; }
    .oes-header p  { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.9rem; }

    /* Tarjetas de métricas */
    div[data-testid="metric-container"] {
        background: #f0f4f8;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        border-left: 4px solid #2d6a9f;
    }

    /* Aviso ético */
    .aviso-etico {
        background: #fff8e1;
        border-left: 4px solid #f9a825;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        font-size: 0.82rem;
        color: #5d4037;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Funciones de acceso a datos ──────────────────────────────────────────────

def get_connection():
    """Retorna una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB, check_same_thread=False)


@st.cache_data(ttl=5)
def cargar_noticias() -> pd.DataFrame:
    """Carga todas las noticias ordenadas por fecha descendente."""
    if not DB.exists():
        return pd.DataFrame()
    with get_connection() as con:
        df = pd.read_sql_query(
            "SELECT * FROM noticias ORDER BY fecha DESC", con
        )
    return df


def insertar_noticia(titulo, institucion, categoria, fuente, fecha, url, resumen):
    """Inserta una noticia nueva. Retorna True si tuvo éxito."""
    try:
        with get_connection() as con:
            con.execute(
                """
                INSERT OR IGNORE INTO noticias
                    (titulo, institucion, categoria, fuente, fecha, url, resumen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (titulo, institucion, categoria, fuente, str(fecha), url, resumen),
            )
        return True
    except Exception as exc:
        st.error(f"Error al insertar: {exc}")
        return False


# ── Cabecera ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="oes-header">
        <h1>🎓 Observatorio de Educación Superior — Prototipo Académico</h1>
        <p>Práctica Guiada N.° 08 · Marketing en la Educación · Monitoreo institucional y regulatorio</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="aviso-etico">⚠️ <strong>Aviso metodológico:</strong> '
    "Los registros de demostración son didácticos. "
    "Confirma cada fuente antes de cualquier uso institucional. "
    "URL, fecha y fuente siempre deben ser visibles (RNF01).</div>",
    unsafe_allow_html=True,
)
st.write("")

# ── Verificar base de datos ──────────────────────────────────────────────────
if not DB.exists():
    st.error(
        "⚠️ Base de datos **oes.db** no encontrada. "
        "Ejecuta primero `python preparar_datos.py` en la misma carpeta."
    )
    st.stop()

# ── Cargar datos ─────────────────────────────────────────────────────────────
df_total = cargar_noticias()

if df_total.empty:
    st.warning("No hay noticias en la base de datos. Ejecuta `preparar_datos.py`.")
    st.stop()

# ── Sidebar: filtros ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Flag_of_Peru.svg/120px-Flag_of_Peru.svg.png",
        width=60,
    )
    st.title("🔎 Filtros")

    # Filtro de categorías
    categorias_disp = sorted(df_total["categoria"].unique().tolist())
    seleccion_cat = st.multiselect(
        "Categoría",
        options=categorias_disp,
        default=categorias_disp,
        help="Selecciona una o más categorías para filtrar.",
    )

    # Filtro de texto libre
    busqueda = st.text_input(
        "Buscar título o institución",
        placeholder="Ej: SUNEDU, becas, investigación…",
    )

    # Filtro por rango de fechas (nivel intermedio)
    st.markdown("---")
    st.subheader("📅 Rango de fechas")
    fechas_disp = pd.to_datetime(df_total["fecha"])
    fecha_min = fechas_disp.min().date()
    fecha_max = fechas_disp.max().date()
    rango = st.date_input(
        "Desde — Hasta",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
    )

    st.markdown("---")
    st.caption("OES · Prototipo local · Sin servicios de pago (RNF02)")

# ── Aplicar filtros ───────────────────────────────────────────────────────────
filtrado = df_total[df_total["categoria"].isin(seleccion_cat)].copy()

# Filtro de texto
if busqueda.strip():
    patron = busqueda.strip()
    mascara = filtrado["titulo"].str.contains(patron, case=False, regex=False) | \
              filtrado["institucion"].str.contains(patron, case=False, regex=False)
    filtrado = filtrado[mascara]

# Filtro de fechas
if isinstance(rango, (list, tuple)) and len(rango) == 2:
    f_ini, f_fin = rango
    filtrado = filtrado[
        (pd.to_datetime(filtrado["fecha"]).dt.date >= f_ini) &
        (pd.to_datetime(filtrado["fecha"]).dt.date <= f_fin)
    ]

# ── RF03: Métricas / indicadores ─────────────────────────────────────────────
st.subheader("📊 Indicadores")
c1, c2, c3, c4 = st.columns(4)
c1.metric("📰 Noticias", len(filtrado))
c2.metric("🏛️ Instituciones", filtrado["institucion"].nunique())
c3.metric("🏷️ Categorías", filtrado["categoria"].nunique())
c4.metric(
    "📆 Rango de fechas",
    f"{filtrado['fecha'].min()} → {filtrado['fecha'].max()}"
    if not filtrado.empty else "—",
)

# ── Gráfico de distribución ──────────────────────────────────────────────────
st.subheader("📈 Distribución por categoría")
if not filtrado.empty:
    conteo = filtrado["categoria"].value_counts().reset_index()
    conteo.columns = ["Categoría", "Cantidad"]
    st.bar_chart(conteo.set_index("Categoría"))
else:
    st.info("No hay resultados con los filtros actuales.")

# Distribución por institución
if not filtrado.empty:
    with st.expander("Ver distribución por institución"):
        conteo_inst = filtrado["institucion"].value_counts().reset_index()
        conteo_inst.columns = ["Institución", "Noticias"]
        st.bar_chart(conteo_inst.set_index("Institución"))

# ── RF02 + RNF01: Tabla de noticias ──────────────────────────────────────────
st.subheader("📋 Noticias registradas")
if filtrado.empty:
    st.warning("⚠️ No se encontraron noticias con los filtros actuales.")
else:
    # Hacer la URL clicable
    df_display = filtrado[
        ["fecha", "institucion", "categoria", "titulo", "fuente", "url", "resumen"]
    ].copy()

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "fecha":       st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
            "institucion": st.column_config.TextColumn("Institución"),
            "categoria":   st.column_config.TextColumn("Categoría"),
            "titulo":      st.column_config.TextColumn("Título", width="large"),
            "fuente":      st.column_config.TextColumn("Fuente"),
            "url":         st.column_config.LinkColumn("URL", display_text="🔗 Ver fuente"),
            "resumen":     st.column_config.TextColumn("Resumen", width="large"),
        },
    )

# ── RF04: Exportar CSV ────────────────────────────────────────────────────────
st.subheader("📥 Exportar resultados")
col_exp, col_info = st.columns([1, 3])
with col_exp:
    st.download_button(
        label="⬇️ Exportar CSV",
        data=filtrado.to_csv(index=False).encode("utf-8-sig"),
        file_name="oes_resultados.csv",
        mime="text/csv",
        help="Descarga los registros filtrados en formato CSV (compatible con Excel).",
    )
with col_info:
    st.caption(
        f"Se exportarán **{len(filtrado)}** registros con los filtros actuales. "
        "El archivo incluye todos los campos, incluida URL y fuente (RNF01)."
    )

# ── RF01: Formulario para agregar nueva noticia ───────────────────────────────
st.markdown("---")
st.subheader("➕ Registrar nueva noticia")

with st.expander("📝 Abrir formulario de registro"):
    st.markdown(
        "Completa **todos** los campos con datos verificados. "
        "La URL debe apuntar directamente a la nota original."
    )

    with st.form("form_nueva_noticia", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            f_titulo      = st.text_input("Título de la noticia *", max_chars=300)
            f_institucion = st.text_input("Institución *", max_chars=150)
            f_categoria   = st.selectbox(
                "Categoría *",
                options=["Ente rector", "Universidad pública", "Universidad privada",
                         "Instituto superior", "Otro"],
            )
            f_fuente      = st.text_input("Fuente (nombre del portal) *", max_chars=200)
        with col_b:
            f_fecha   = st.date_input("Fecha de publicación *", value=date.today())
            f_url     = st.text_input("URL directa a la nota *", placeholder="https://…")
            f_resumen = st.text_area(
                "Resumen redactado y verificado *",
                max_chars=500,
                height=120,
                placeholder="Escribe el resumen con tus propias palabras, confirmando la fuente.",
            )

        enviado = st.form_submit_button("💾 Registrar noticia")

    if enviado:
        campos_vacios = [
            n for n, v in [
                ("Título", f_titulo), ("Institución", f_institucion),
                ("Fuente", f_fuente), ("URL", f_url), ("Resumen", f_resumen),
            ] if not v.strip()
        ]
        if campos_vacios:
            st.error(f"Faltan campos obligatorios: {', '.join(campos_vacios)}")
        elif not f_url.startswith("http"):
            st.error("La URL debe comenzar con http:// o https://")
        else:
            ok = insertar_noticia(
                f_titulo.strip(), f_institucion.strip(), f_categoria,
                f_fuente.strip(), f_fecha, f_url.strip(), f_resumen.strip(),
            )
            if ok:
                st.success(
                    f"✅ Noticia **{f_titulo[:60]}…** registrada correctamente. "
                    "Refresca la página (F5) para ver el nuevo registro."
                )
                st.cache_data.clear()

# ── Pie de página ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <small>
    <strong>OES — Prototipo Académico</strong> · Práctica Guiada N.° 08 ·
    Tecnologías: Python 3.11+ · SQLite · Streamlit · Pandas<br>
    Referencias: <a href="https://observatorio.com.pe/" target="_blank">observatorio.com.pe</a> ·
    <a href="https://docs.streamlit.io/" target="_blank">docs.streamlit.io</a> ·
    <a href="https://docs.python.org/3/library/sqlite3.html" target="_blank">sqlite3 docs</a><br>
    <em>Advertencia metodológica: implementación educativa original;
    no reproduce el código fuente real del OES comercial.</em>
    </small>
    """,
    unsafe_allow_html=True,
)

