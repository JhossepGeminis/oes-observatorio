"""
app.py — Observatorio de Educación Superior (OES)
Prototipo académico — Práctica Guiada N.° 08
Tecnologías: Python 3.11+, SQLite, Streamlit, Pandas, Plotly

Requisitos cubiertos:
  RF01 · Registrar noticia (formulario con validación completa)
  RF02 · Filtrar por categoría, institución y texto libre
  RF03 · Calcular indicadores y visualizar con gráficos interactivos (Plotly)
  RF04 · Exportar resultados a CSV
  RNF01 · Trazabilidad: URL, fecha y fuente siempre visibles
  RNF02 · Funcionamiento 100 % local, sin servicios de pago
"""

import sqlite3
from pathlib import Path
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════
DB = Path(__file__).with_name("oes.db")

st.set_page_config(
    page_title="OES — Observatorio de Educación Superior",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Prototipo académico OES · Práctica Guiada N.° 08 · Python + Streamlit",
    },
)

# Paleta de colores institucional
AZUL_OSCURO  = "#0d2b4e"
AZUL_MED     = "#1a4f82"
AZUL_CLARO   = "#2d7dd2"
ACENTO       = "#e8a020"
FONDO_CARD   = "#f5f8fc"
TEXTO_GRIS   = "#4a5568"

COLORES_CAT = {
    "Ente rector":        "#2d7dd2",
    "Universidad pública":"#2ecc71",
    "Universidad privada":"#9b59b6",
    "Instituto superior": "#e67e22",
    "Otro":               "#95a5a6",
}

# ═══════════════════════════════════════════════════════════════════════════════
# CSS GLOBAL
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
  /* ── Tipografía e importación ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Inter', 'Segoe UI', sans-serif;
  }}

  /* ── Fondo general ── */
  .stApp {{
      background: #f0f4f8;
  }}

  /* ── Hero header ── */
  .hero-banner {{
      background: linear-gradient(135deg, {AZUL_OSCURO} 0%, {AZUL_MED} 55%, {AZUL_CLARO} 100%);
      border-radius: 16px;
      padding: 2rem 2.5rem 1.8rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 8px 32px rgba(13,43,78,0.18);
      position: relative;
      overflow: hidden;
  }}
  .hero-banner::after {{
      content: "";
      position: absolute;
      top: -40px; right: -40px;
      width: 200px; height: 200px;
      background: rgba(255,255,255,0.05);
      border-radius: 50%;
  }}
  .hero-title {{
      color: #ffffff;
      font-size: 1.75rem;
      font-weight: 700;
      margin: 0 0 0.3rem;
      letter-spacing: -0.3px;
  }}
  .hero-sub {{
      color: rgba(255,255,255,0.80);
      font-size: 0.88rem;
      margin: 0;
      font-weight: 400;
  }}
  .hero-badge {{
      display: inline-block;
      background: {ACENTO};
      color: #fff;
      border-radius: 20px;
      padding: 2px 10px;
      font-size: 0.72rem;
      font-weight: 600;
      margin-top: 0.6rem;
      letter-spacing: 0.5px;
  }}

  /* ── Tarjetas de métricas ── */
  .kpi-wrap {{
      background: #ffffff;
      border-radius: 14px;
      padding: 1.1rem 1.3rem;
      box-shadow: 0 2px 12px rgba(0,0,0,0.07);
      border-top: 4px solid {AZUL_CLARO};
      text-align: center;
      transition: transform .15s, box-shadow .15s;
  }}
  .kpi-wrap:hover {{
      transform: translateY(-3px);
      box-shadow: 0 6px 20px rgba(0,0,0,0.11);
  }}
  .kpi-icon {{ font-size: 1.9rem; margin-bottom: 0.3rem; }}
  .kpi-value {{
      font-size: 2.1rem;
      font-weight: 700;
      color: {AZUL_OSCURO};
      line-height: 1;
  }}
  .kpi-label {{
      font-size: 0.78rem;
      color: {TEXTO_GRIS};
      font-weight: 500;
      margin-top: 0.25rem;
      text-transform: uppercase;
      letter-spacing: 0.6px;
  }}

  /* ── Secciones ── */
  .section-header {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      border-bottom: 2px solid #dbe4ee;
      padding-bottom: 0.5rem;
      margin: 1.6rem 0 1rem;
  }}
  .section-header h3 {{
      margin: 0;
      font-size: 1.1rem;
      font-weight: 600;
      color: {AZUL_OSCURO};
  }}
  .section-icon {{
      font-size: 1.3rem;
  }}

  /* ── Aviso ético ── */
  .aviso {{
      background: #fffbeb;
      border-left: 4px solid {ACENTO};
      padding: 0.65rem 1rem;
      border-radius: 0 8px 8px 0;
      font-size: 0.82rem;
      color: #78350f;
      margin-bottom: 0.5rem;
  }}

  /* ── Badge de categoría ── */
  .badge {{
      display: inline-block;
      border-radius: 12px;
      padding: 2px 9px;
      font-size: 0.72rem;
      font-weight: 600;
      color: #fff;
  }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
      background: {AZUL_OSCURO} !important;
  }}
  [data-testid="stSidebar"] * {{
      color: #d4e3f7 !important;
  }}
  [data-testid="stSidebar"] .stMultiSelect label,
  [data-testid="stSidebar"] .stTextInput label,
  [data-testid="stSidebar"] .stDateInput label {{
      color: #90b8e0 !important;
      font-size: 0.8rem !important;
      font-weight: 500 !important;
      text-transform: uppercase;
      letter-spacing: 0.5px;
  }}
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 {{
      color: #ffffff !important;
  }}
  [data-testid="stSidebar"] hr {{
      border-color: rgba(255,255,255,0.12) !important;
  }}

  /* ── Dataframe ── */
  .stDataFrame {{ border-radius: 10px; overflow: hidden; }}

  /* ── Botón primario ── */
  .stDownloadButton > button, .stFormSubmitButton > button {{
      background: linear-gradient(135deg, {AZUL_MED}, {AZUL_CLARO}) !important;
      color: white !important;
      border: none !important;
      border-radius: 8px !important;
      font-weight: 600 !important;
      padding: 0.5rem 1.4rem !important;
      transition: opacity .2s !important;
  }}
  .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {{
      opacity: 0.88 !important;
  }}

  /* ── Footer ── */
  .footer {{
      background: #fff;
      border-radius: 12px;
      padding: 1.1rem 1.5rem;
      margin-top: 2rem;
      box-shadow: 0 2px 10px rgba(0,0,0,0.05);
      font-size: 0.8rem;
      color: {TEXTO_GRIS};
      text-align: center;
  }}
  .footer a {{ color: {AZUL_CLARO}; text-decoration: none; }}
  .footer a:hover {{ text-decoration: underline; }}

  /* ── Expander mejorado ── */
  .streamlit-expanderHeader {{
      background: #eef3fb !important;
      border-radius: 8px !important;
      font-weight: 600 !important;
  }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# BASE DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════
def get_connection():
    return sqlite3.connect(DB, check_same_thread=False)

@st.cache_data(ttl=5)
def cargar_noticias() -> pd.DataFrame:
    if not DB.exists():
        return pd.DataFrame()
    with get_connection() as con:
        df = pd.read_sql_query("SELECT * FROM noticias ORDER BY fecha DESC", con)
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
    return df

def insertar_noticia(titulo, institucion, categoria, fuente, fecha, url, resumen):
    try:
        with get_connection() as con:
            con.execute(
                "INSERT OR IGNORE INTO noticias "
                "(titulo,institucion,categoria,fuente,fecha,url,resumen) "
                "VALUES (?,?,?,?,?,?,?)",
                (titulo, institucion, categoria, fuente, str(fecha), url, resumen),
            )
        return True
    except Exception as exc:
        st.error(f"Error al insertar: {exc}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-banner">
  <div class="hero-title">🎓 Observatorio de Educación Superior</div>
  <p class="hero-sub">
    Plataforma de monitoreo institucional y regulatorio · Educación Superior Peruana
  </p>
  <span class="hero-badge">Práctica Guiada N.° 08 — Prototipo Académico</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="aviso">
  ⚠️ <strong>Aviso metodológico:</strong> Los registros de demostración son didácticos.
  Verifica cada fuente antes de cualquier uso institucional.
  URL, fecha y fuente son siempre visibles <em>(RNF01)</em>.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICAR DB
# ═══════════════════════════════════════════════════════════════════════════════
if not DB.exists():
    st.error("⚠️ **oes.db** no encontrada. Ejecuta `python preparar_datos.py` primero.")
    st.stop()

df_total = cargar_noticias()
if df_total.empty:
    st.warning("No hay noticias en la base de datos. Ejecuta `preparar_datos.py`.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
      <div style='font-size:2.8rem;'>🎓</div>
      <div style='font-size:1rem; font-weight:700; color:#fff; margin-top:0.3rem;'>OES Perú</div>
      <div style='font-size:0.72rem; color:#90b8e0;'>Observatorio Educativo</div>
    </div>
    <hr/>
    """, unsafe_allow_html=True)

    st.markdown("### 🔍 Filtros")

    categorias_disp = sorted(df_total["categoria"].unique().tolist())
    seleccion_cat = st.multiselect(
        "Categoría",
        options=categorias_disp,
        default=categorias_disp,
    )

    instituciones_disp = ["Todas"] + sorted(df_total["institucion"].unique().tolist())
    sel_inst = st.selectbox("Institución", instituciones_disp)

    busqueda = st.text_input("🔎 Buscar", placeholder="Título, institución…")

    st.markdown("---")
    st.markdown("### 📅 Rango de fechas")
    fechas_dt = df_total["fecha"]
    fecha_min = fechas_dt.min().date()
    fecha_max = fechas_dt.max().date()
    rango = st.date_input(
        "Desde — Hasta",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#6b8fb5; text-align:center; padding-bottom:0.5rem;'>
      🔒 Sin servicios externos · SQLite local<br>
      OES · Práctica N.° 08
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# APLICAR FILTROS
# ═══════════════════════════════════════════════════════════════════════════════
filtrado = df_total[df_total["categoria"].isin(seleccion_cat)].copy()

if sel_inst != "Todas":
    filtrado = filtrado[filtrado["institucion"] == sel_inst]

if busqueda.strip():
    p = busqueda.strip()
    mask = (
        filtrado["titulo"].str.contains(p, case=False, regex=False) |
        filtrado["institucion"].str.contains(p, case=False, regex=False) |
        filtrado["resumen"].str.contains(p, case=False, regex=False)
    )
    filtrado = filtrado[mask]

if isinstance(rango, (list, tuple)) and len(rango) == 2:
    f_ini, f_fin = pd.Timestamp(rango[0]), pd.Timestamp(rango[1])
    filtrado = filtrado[
        (filtrado["fecha"] >= f_ini) & (filtrado["fecha"] <= f_fin)
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# KPIs — RF03
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><span class="section-icon">📊</span><h3>Indicadores clave</h3></div>', unsafe_allow_html=True)

delta_total = len(filtrado) - len(df_total)
rango_str = (
    f"{filtrado['fecha'].min().strftime('%d/%m/%Y')} – {filtrado['fecha'].max().strftime('%d/%m/%Y')}"
    if not filtrado.empty else "—"
)

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "📰", len(filtrado),                     "Noticias filtradas"),
    (k2, "🏛️", filtrado["institucion"].nunique(), "Instituciones"),
    (k3, "🏷️", filtrado["categoria"].nunique(),   "Categorías"),
    (k4, "📅", rango_str,                          "Período cubierto"),
]
for col, icon, val, label in kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-wrap">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")


# ═══════════════════════════════════════════════════════════════════════════════
# GRÁFICOS — RF03
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><span class="section-icon">📈</span><h3>Análisis y visualizaciones</h3></div>', unsafe_allow_html=True)

if filtrado.empty:
    st.info("🔍 Sin resultados para los filtros actuales.")
else:
    col_g1, col_g2 = st.columns(2)

    # ── Gráfico 1: Donut por categoría ──
    with col_g1:
        conteo_cat = filtrado["categoria"].value_counts().reset_index()
        conteo_cat.columns = ["Categoría", "Cantidad"]
        colores_cat = [COLORES_CAT.get(c, "#95a5a6") for c in conteo_cat["Categoría"]]

        fig_donut = go.Figure(go.Pie(
            labels=conteo_cat["Categoría"],
            values=conteo_cat["Cantidad"],
            hole=0.52,
            marker=dict(colors=colores_cat, line=dict(color="#fff", width=2)),
            textinfo="label+percent",
            textfont=dict(size=11),
            hovertemplate="<b>%{label}</b><br>Noticias: %{value}<br>%{percent}<extra></extra>",
        ))
        fig_donut.update_layout(
            title=dict(text="Distribución por categoría", font=dict(size=13, color=AZUL_OSCURO), x=0.5),
            showlegend=False,
            margin=dict(t=50, b=10, l=10, r=10),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=f"<b>{len(filtrado)}</b><br>noticias",
                              x=0.5, y=0.5, font_size=14, showarrow=False,
                              font=dict(color=AZUL_OSCURO))],
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # ── Gráfico 2: Barras horizontales por institución ──
    with col_g2:
        conteo_inst = (
            filtrado["institucion"].value_counts()
            .reset_index()
            .rename(columns={"institucion": "Institución", "count": "Noticias"})
            .head(10)
        )
        fig_bar = px.bar(
            conteo_inst,
            x="Noticias",
            y="Institución",
            orientation="h",
            color="Noticias",
            color_continuous_scale=[[0, "#bed8f7"], [1, AZUL_MED]],
            text="Noticias",
        )
        fig_bar.update_traces(textposition="outside", textfont_size=11)
        fig_bar.update_layout(
            title=dict(text="Noticias por institución (Top 10)", font=dict(size=13, color=AZUL_OSCURO), x=0.5),
            yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
            xaxis_title="",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(t=50, b=10, l=10, r=40),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        fig_bar.update_xaxes(showgrid=True, gridcolor="#e8edf2")
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Gráfico 3: Línea temporal ──
    col_g3, col_g4 = st.columns(2)

    with col_g3:
        serie_tiempo = (
            filtrado.set_index("fecha")
            .resample("D")["id"]
            .count()
            .reset_index()
            .rename(columns={"fecha": "Fecha", "id": "Noticias"})
        )
        fig_line = px.area(
            serie_tiempo,
            x="Fecha",
            y="Noticias",
            color_discrete_sequence=[AZUL_CLARO],
            markers=True,
        )
        fig_line.update_traces(
            line=dict(width=2.5),
            marker=dict(size=6, color=AZUL_MED),
            fillcolor=f"rgba(45,125,210,0.12)",
        )
        fig_line.update_layout(
            title=dict(text="Volumen de noticias en el tiempo", font=dict(size=13, color=AZUL_OSCURO), x=0.5),
            xaxis_title="",
            yaxis_title="Noticias",
            margin=dict(t=50, b=10, l=10, r=10),
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        fig_line.update_xaxes(showgrid=False)
        fig_line.update_yaxes(showgrid=True, gridcolor="#e8edf2", dtick=1)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_g4:
        # Treemap: institución × categoría
        fig_tree = px.treemap(
            filtrado,
            path=["categoria", "institucion"],
            color="categoria",
            color_discrete_map=COLORES_CAT,
            title="Mapa de cobertura (categoría → institución)",
        )
        fig_tree.update_traces(
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>Noticias: %{value}<extra></extra>",
        )
        fig_tree.update_layout(
            title=dict(font=dict(size=13, color=AZUL_OSCURO), x=0.5),
            margin=dict(t=50, b=0, l=0, r=0),
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_tree, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TABLA DE NOTICIAS — RF02 + RNF01
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><span class="section-icon">📋</span><h3>Noticias registradas</h3></div>', unsafe_allow_html=True)

if filtrado.empty:
    st.warning("⚠️ No se encontraron noticias con los filtros actuales.")
else:
    df_display = filtrado[["fecha","institucion","categoria","titulo","fuente","url","resumen"]].copy()
    df_display["fecha"] = df_display["fecha"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=380,
        column_config={
            "fecha":       st.column_config.TextColumn("📅 Fecha", width=100),
            "institucion": st.column_config.TextColumn("🏛️ Institución", width=160),
            "categoria":   st.column_config.TextColumn("🏷️ Categoría", width=140),
            "titulo":      st.column_config.TextColumn("📰 Título", width="large"),
            "fuente":      st.column_config.TextColumn("📡 Fuente", width=160),
            "url":         st.column_config.LinkColumn("🔗 URL", display_text="Ver fuente →", width=120),
            "resumen":     st.column_config.TextColumn("📝 Resumen", width="large"),
        },
    )

    # ── RF04: Exportar ──
    col_dl, col_info = st.columns([1, 4])
    with col_dl:
        st.download_button(
            label="⬇️  Exportar CSV",
            data=filtrado.assign(fecha=filtrado["fecha"].dt.strftime("%Y-%m-%d"))
                         .to_csv(index=False).encode("utf-8-sig"),
            file_name=f"oes_resultados_{date.today()}.csv",
            mime="text/csv",
        )
    with col_info:
        st.caption(
            f"📦 **{len(filtrado)}** registros listos para exportar · "
            "Incluye todos los campos con URL y fuente *(RNF01)*"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FORMULARIO DE REGISTRO — RF01
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><span class="section-icon">➕</span><h3>Registrar nueva noticia</h3></div>', unsafe_allow_html=True)

with st.expander("📝  Abrir formulario de registro verificado", expanded=False):
    st.markdown("""
    <div style='background:#eef3fb; border-radius:8px; padding:0.7rem 1rem; margin-bottom:1rem;
         font-size:0.84rem; color:#1a4f82;'>
      📌 Completa <strong>todos</strong> los campos con datos verificados en fuentes oficiales.
      La URL debe apuntar <strong>directamente</strong> a la nota original — no a la portada del sitio.
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_nueva_noticia", clear_on_submit=True):
        c_a, c_b = st.columns(2)
        with c_a:
            f_titulo      = st.text_input("📰 Título de la noticia *", max_chars=300,
                                          placeholder="Titular exacto de la nota")
            f_institucion = st.text_input("🏛️ Institución *", max_chars=150,
                                          placeholder="Ej: SUNEDU, UNMSM, PUCP…")
            f_categoria   = st.selectbox(
                "🏷️ Categoría *",
                ["Ente rector", "Universidad pública", "Universidad privada",
                 "Instituto superior", "Otro"],
            )
            f_fuente      = st.text_input("📡 Fuente (nombre del portal) *", max_chars=200,
                                          placeholder="Ej: Portal MINEDU")
        with c_b:
            f_fecha   = st.date_input("📅 Fecha de publicación *", value=date.today())
            f_url     = st.text_input("🔗 URL directa a la nota *", placeholder="https://…")
            f_resumen = st.text_area(
                "📝 Resumen verificado *", max_chars=500, height=130,
                placeholder="Redacta con tus propias palabras. Confirma que el resumen refleja la nota original.",
            )

        col_btn, col_note = st.columns([1, 3])
        with col_btn:
            enviado = st.form_submit_button("💾  Guardar noticia", use_container_width=True)
        with col_note:
            st.caption("⚠️ No registres noticias no verificadas ni URLs de portadas genéricas.")

    if enviado:
        vacios = [n for n, v in [
            ("Título", f_titulo), ("Institución", f_institucion),
            ("Fuente", f_fuente), ("URL", f_url), ("Resumen", f_resumen),
        ] if not v.strip()]

        if vacios:
            st.error(f"❌ Campos obligatorios vacíos: **{', '.join(vacios)}**")
        elif not f_url.strip().startswith("http"):
            st.error("❌ La URL debe comenzar con `http://` o `https://`")
        else:
            ok = insertar_noticia(
                f_titulo.strip(), f_institucion.strip(), f_categoria,
                f_fuente.strip(), f_fecha, f_url.strip(), f_resumen.strip(),
            )
            if ok:
                st.success(f"✅ Noticia registrada correctamente. Recarga la página para verla.")
                st.cache_data.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <strong>🎓 OES — Observatorio de Educación Superior · Prototipo Académico</strong><br>
  Práctica Guiada N.° 08 · Marketing en la Educación Superior · Python 3.11+ · SQLite · Streamlit · Plotly<br>
  Referencias:
  <a href="https://observatorio.com.pe/" target="_blank">observatorio.com.pe</a> ·
  <a href="https://docs.streamlit.io/" target="_blank">docs.streamlit.io</a> ·
  <a href="https://plotly.com/python/" target="_blank">plotly.com</a> ·
  <a href="https://docs.python.org/3/library/sqlite3.html" target="_blank">sqlite3 docs</a><br>
  <em style="color:#94a3b8;">
    Implementación educativa original — no reproduce el código fuente real del OES comercial.
  </em>
</div>
""", unsafe_allow_html=True)
