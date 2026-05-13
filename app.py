import streamlit as st
from db import load_becarios, load_perdidas, load_egresados, load_notas, load_orden_merito
from secciones import resumen, matricula, perdidas, egresados, notas, orden_merito
st.set_page_config(
    page_title="Dashboard Becas UPCH",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --accent:        #2D7D8E;
    --accent-soft:   rgba(45,125,142,0.10);
    --accent-ink:    #1A515B;
    --positive:      #16A34A;
    --positive-soft: rgba(22,163,74,0.12);
    --warning:       #D97706;
    --warning-soft:  rgba(217,119,6,0.14);
    --danger:        #DC2626;
    --danger-soft:   rgba(220,38,38,0.10);
    --violet:        #7C3AED;
    --info:          #3B82F6;
    --bg:            #F9F8F7;
    --surface:       #FFFFFF;
    --surface-2:     #F3F1EE;
    --border:        #E8E5E1;
    --border-strong: #D5D1CB;
    --ink:           #1C1917;
    --ink-2:         #44403C;
    --ink-3:         #78716C;
    --ink-4:         #A8A29E;
    --r:             10px;
    --r-sm:          6px;
    --shadow:        0 1px 3px rgba(20,25,30,.05), 0 1px 2px rgba(20,25,30,.03);
    --font-sans:     'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif;
    --font-mono:     'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: var(--font-sans) !important;
    -webkit-font-smoothing: antialiased;
}
.stApp { background-color: var(--bg) !important; }
.main .block-container,
[data-testid="block-container"] {
    background-color: var(--bg) !important;
    padding-top: 24px !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-sans) !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: var(--ink-2) !important; font-size: 13px !important; }
[data-testid="stSidebar"] h2 {
    font-size: 14px !important; font-weight: 700 !important;
    color: var(--ink) !important; letter-spacing: -0.01em !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; margin: 10px 0 !important; }
[data-testid="stSidebar"] .stCaption p { color: var(--ink-4) !important; font-size: 11px !important; }
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stMultiSelect > div > div {
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    background: var(--bg) !important;
    font-size: 12.5px !important;
}

/* ── Typography ── */
h1 {
    font-family: var(--font-sans) !important; font-size: 24px !important;
    font-weight: 700 !important; letter-spacing: -0.018em !important;
    color: var(--ink) !important; margin-bottom: 2px !important;
}
h2 { font-size: 18px !important; font-weight: 700 !important; color: var(--ink) !important; }
h3 { font-size: 15px !important; font-weight: 600 !important; color: var(--ink) !important; }
.stCaption p { color: var(--ink-3) !important; font-size: 12px !important; }

/* ── KPI Cards ── */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r);
    padding: 14px 16px;
    display: flex; flex-direction: column; gap: 4px;
    position: relative; min-height: 92px;
    box-shadow: var(--shadow);
    overflow: hidden; margin-bottom: 2px;
}
.kpi-accent-bar {
    position: absolute; left: 0; top: 12px; bottom: 12px;
    width: 3px; border-radius: 0 3px 3px 0;
    background: var(--kpi-accent, var(--accent));
}
.kpi-label {
    font-size: 10.5px; font-weight: 600; color: var(--ink-3);
    text-transform: uppercase; letter-spacing: 0.07em;
    padding-left: 6px; font-family: var(--font-sans);
}
.kpi-value {
    font-family: var(--font-mono) !important;
    font-size: 26px; font-weight: 700;
    letter-spacing: -0.025em; color: var(--ink);
    line-height: 1.1; font-feature-settings: "tnum" 1;
    padding-left: 6px;
}
.kpi-delta {
    font-size: 11.5px; color: var(--ink-4);
    padding-left: 6px; font-family: var(--font-sans);
}
.kpi-delta.up   { color: var(--positive); }
.kpi-delta.down { color: var(--danger); }

/* ── Section/panel titles ── */
.section-title {
    font-size: 13px !important; font-weight: 600 !important;
    color: var(--ink) !important; letter-spacing: -0.005em !important;
    margin: 0 0 8px 0 !important; padding: 0 !important;
    font-family: var(--font-sans) !important;
}

/* ── Inputs ── */
.stTextInput input {
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    background: var(--surface) !important;
    font-family: var(--font-sans) !important;
    color: var(--ink) !important; font-size: 13px !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-soft) !important;
    outline: none !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    background: var(--surface) !important;
    font-family: var(--font-sans) !important; font-size: 13px !important;
}

/* ── Buttons ── */
.stDownloadButton button {
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--ink) !important; border-radius: var(--r-sm) !important;
    font-family: var(--font-sans) !important;
    font-size: 12.5px !important; font-weight: 500 !important;
    box-shadow: var(--shadow) !important;
}
.stDownloadButton button:hover { border-color: var(--border-strong) !important; }

/* ── Chart frames ── */
[data-testid="stPlotlyChart"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow) !important;
    padding: 16px 16px 28px !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    overflow: hidden !important; box-shadow: var(--shadow) !important;
}

/* ── Misc ── */
.stSpinner > div { color: var(--accent) !important; }
hr { border-color: var(--border) !important; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb {
    background: var(--border-strong); border-radius: 4px;
    border: 2px solid var(--bg);
}
::-webkit-scrollbar-track { background: transparent; }
#MainMenu, footer { visibility: hidden; }
[data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


def limpiar_carrera(nombre):
    if not isinstance(nombre, str):
        return nombre
    prefijos = ["CARRERA PROFESIONAL DE ", "CARRERA PROFESIONAL EN ", "CARRERA DE ", "CARRERA EN "]
    for p in prefijos:
        if nombre.upper().startswith(p):
            return nombre[len(p):].strip().title()
    return nombre.strip().title()


with st.spinner("Cargando datos..."):
    df_bec = load_becarios()

df_bec["carrera"] = df_bec["carrera"].apply(limpiar_carrera)

SEMESTRES = sorted(df_bec["semestre_registro"].dropna().unique().tolist(), reverse=True)

with st.sidebar:
    st.markdown("## Beneficios UPCH")
    st.markdown("##### Dahboards")
    st.markdown("---")

    page = st.radio(
        "Sección",
        ["Resumen General", "Matrícula", "Pérdidas de Beca",
         "Egresados", "Notas", "Orden de Mérito"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Filtros**")
    default_sem = SEMESTRES.index("2025-2") if "2025-2" in SEMESTRES else 0
    semestre_sel = st.selectbox("Semestre", SEMESTRES, index=default_sem)
    carreras        = sorted(df_bec["carrera"].dropna().unique().tolist())
    carrera_sel     = st.multiselect("Carrera", carreras, placeholder="Todas")
    financiadores   = sorted(df_bec["financiador"].dropna().unique().tolist())
    financiador_sel = st.multiselect("Financiador", financiadores, placeholder="Todos")
    st.markdown("---")

sem_label = semestre_sel

if page == "Resumen General":
    st.title("Resumen general de becarios")
    st.caption(f"Vista consolidada · UPCH · {sem_label}")
    resumen.render(df_bec, semestre_sel, carrera_sel, financiador_sel)

elif page == "Matrícula":
    st.title("Matrícula de becarios")
    st.caption(f"Estado de matrícula del semestre activo · {sem_label}")
    matricula.render(df_bec, None, semestre_sel, carrera_sel, financiador_sel)

elif page == "Pérdidas de Beca":
    st.title("Pérdidas de beca")
    st.caption(f"Becarios con pérdida por rendimiento · {sem_label}")
    with st.spinner("Cargando datos..."):
        df_per = load_perdidas()
    df_per["nombre_carrera"] = df_per["nombre_carrera"].apply(limpiar_carrera)
    perdidas.render(df_bec, df_per, semestre_sel, carrera_sel, financiador_sel)

elif page == "Egresados":
    st.title("Egresados")
    st.caption(f"Becarios egresados por semestre · {sem_label}")
    with st.spinner("Cargando datos..."):
        df_egr = load_egresados()
    egresados.render(df_egr, semestre_sel, carrera_sel, financiador_sel)

elif page == "Notas":
    st.title("Cursos desaprobados")
    st.caption(f"Becarios con cursos desaprobados · {sem_label}")
    with st.spinner("Cargando datos..."):
        df_not = load_notas()
    notas.render(df_bec, df_not, semestre_sel, carrera_sel, financiador_sel)

elif page == "Orden de Mérito":
    st.title("Orden de mérito")
    st.caption(f"Promedios y ranking académico · {sem_label}")
    with st.spinner("Cargando datos..."):
        df_om = load_orden_merito()
    orden_merito.render(df_bec, df_om, semestre_sel, carrera_sel, financiador_sel)
