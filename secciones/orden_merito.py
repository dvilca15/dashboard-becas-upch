import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import df_to_excel_bytes, df_to_csv_bytes
from theme import (
    metric_card, section_title, plotly_layout,
    TEAL, EMERALD, DANGER, AMBER, VIOLET,
)

ORDEN_SEMESTRES = [
    "2024-1", "2024-2",
    "20241-20242",
    "20242-20251",
    "2025-1", "2025-2",
    "20251-20252",
]


def limpiar_carrera(nombre):
    if not isinstance(nombre, str):
        return nombre
    prefijos = ["CARRERA PROFESIONAL DE ", "CARRERA PROFESIONAL EN ", "CARRERA DE ", "CARRERA EN "]
    for p in prefijos:
        if nombre.upper().startswith(p):
            return nombre[len(p):].strip().title()
    return nombre.strip().title()


def render(df_bec, df_om, semestre_sel, carrera_sel, financiador_sel):
    df_om = df_om.copy()
    df_om["carrera"] = df_om["carrera"].apply(limpiar_carrera)

    df_act = df_bec[df_bec["estado_beneficiario"] == "ACTIVO"].copy()
    if semestre_sel != "Todos":
        df_act = df_act[df_act["semestre_registro"] == semestre_sel]
    if carrera_sel:
        df_act = df_act[df_act["carrera"].isin(carrera_sel)]
    if financiador_sel:
        df_act = df_act[df_act["financiador"].isin(financiador_sel)]

    df_act["dni_str"] = df_act["dni"].astype(str).str.strip()
    df_om["dni_str"]  = df_om["dni"].astype(str).str.strip()
    dnis_activos = set(df_act["dni_str"].unique())

    df_om_bec = df_om[df_om["dni_str"].isin(dnis_activos)].copy()
    df_om_bec["nota_promedio"] = pd.to_numeric(df_om_bec["nota_promedio"], errors="coerce")
    df_om_bec = df_om_bec[df_om_bec["nota_promedio"].between(0, 20) | df_om_bec["nota_promedio"].isna()]

    semestres_om_disp = [s for s in ORDEN_SEMESTRES if s in df_om_bec["semestre"].unique()]
    otros = [s for s in df_om_bec["semestre"].unique() if s not in ORDEN_SEMESTRES]
    semestres_om_disp = semestres_om_disp + sorted(otros)

    total_activos = len(df_act)

    sem_om_sel = st.selectbox(
        "Ver orden de mérito del semestre",
        ["Todos"] + semestres_om_disp,
        key="sel_sem_om",
        help="Filtra todos los gráficos y KPIs por semestre de OM.",
    )
    df_view = df_om_bec if sem_om_sel == "Todos" else df_om_bec[df_om_bec["semestre"] == sem_om_sel]

    con_om_view  = df_view["dni_str"].nunique()
    sin_om_view  = total_activos - con_om_view
    pct_om_view  = f"{(con_om_view/total_activos*100):.1f}%" if total_activos > 0 else "0%"
    prom_general = df_view["nota_promedio"].mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card(f"{total_activos:,}", "Becarios activos", accent=TEAL)
    with c2: metric_card(
        f"{con_om_view:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {pct_om_view}</span>",
        "Con orden de mérito", accent=EMERALD,
    )
    with c3: metric_card(f"{sin_om_view:,}", "Sin orden de mérito", accent=DANGER)
    with c4: metric_card(
        f"{prom_general:.2f}" if pd.notna(prom_general) else "—",
        "Promedio general", accent=AMBER,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        section_title("Distribución de nota promedio")
        fig = px.histogram(
            df_view.dropna(subset=["nota_promedio"]), x="nota_promedio",
            nbins=40, color_discrete_sequence=[TEAL],
        )
        fig.update_traces(marker_line_width=0, opacity=0.9)
        fig.update_layout(**plotly_layout(
            height=300,
            xaxis=dict(title_text="Nota promedio"),
            yaxis=dict(title_text="Cantidad"),
            showlegend=False,
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Décimo, quinto y tercio superior por semestre")
        filas = []
        for sem in semestres_om_disp:
            df_s = df_om_bec[df_om_bec["semestre"] == sem]
            dec = (df_s["decimo_superior"].str.upper() == "SI").sum() if "decimo_superior" in df_s.columns else 0
            qui = (df_s["quinto_superior"].str.upper() == "SI").sum() if "quinto_superior" in df_s.columns else 0
            ter = (df_s["tercio_superior"].str.upper() == "SI").sum() if "tercio_superior" in df_s.columns else 0
            filas.append({"Semestre": sem, "Décimo superior": dec, "Quinto superior": qui, "Tercio superior": ter})
        df_sup = pd.DataFrame(filas)
        if len(df_sup) > 0:
            max_val = df_sup[["Décimo superior", "Quinto superior", "Tercio superior"]].max().max()
            fig = go.Figure()
            fig.add_bar(x=df_sup["Semestre"], y=df_sup["Décimo superior"],
                        name="Décimo superior", marker_color=TEAL,
                        text=df_sup["Décimo superior"], textposition="outside",
                        textfont=dict(size=10, family="JetBrains Mono"))
            fig.add_bar(x=df_sup["Semestre"], y=df_sup["Quinto superior"],
                        name="Quinto superior", marker_color=EMERALD,
                        text=df_sup["Quinto superior"], textposition="outside",
                        textfont=dict(size=10, family="JetBrains Mono"))
            fig.add_bar(x=df_sup["Semestre"], y=df_sup["Tercio superior"],
                        name="Tercio superior", marker_color=AMBER,
                        text=df_sup["Tercio superior"], textposition="outside",
                        textfont=dict(size=10, family="JetBrains Mono"))
            fig.update_layout(**plotly_layout(
                barmode="group", height=300,
                xaxis=dict(type="category"),
                yaxis=dict(range=[0, max_val * 1.3]),
            ))
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_title("Promedio por carrera (top 10)")
        if len(df_view) > 0:
            prom_carr = (df_view.groupby("carrera")["nota_promedio"]
                         .mean().sort_values(ascending=False).head(10).reset_index())
            prom_carr.columns = ["Carrera", "Promedio"]
            prom_carr["Promedio"] = prom_carr["Promedio"].round(2)
            fig = px.bar(prom_carr, x="Promedio", y="Carrera", orientation="h",
                         color_discrete_sequence=[VIOLET], text="Promedio")
            fig.update_traces(textposition="outside", textangle=0,
                              textfont=dict(size=10, family="JetBrains Mono"),
                              marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=380,
                xaxis=dict(range=[0, 22], visible=False),
                yaxis=dict(autorange="reversed", tickfont=dict(size=9)),
                showlegend=False,
            ))
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_title("Promedio general por semestre (histórico)")
        prom_sem = []
        for sem in semestres_om_disp:
            prom = df_om_bec[df_om_bec["semestre"] == sem]["nota_promedio"].mean()
            prom_sem.append({"Semestre": sem, "Promedio": round(prom, 2) if pd.notna(prom) else 0})
        df_prom_sem = pd.DataFrame(prom_sem)
        fig = px.bar(df_prom_sem, x="Semestre", y="Promedio",
                     color_discrete_sequence=[AMBER], text="Promedio")
        fig.update_traces(textposition="outside",
                          textfont=dict(size=10, family="JetBrains Mono"),
                          marker_line_width=0)
        fig.update_layout(**plotly_layout(
            height=320, showlegend=False,
            xaxis=dict(type="category"),
            yaxis=dict(range=[0, 20]),
        ))
        st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)

    with col5:
        section_title("Top 10 becarios por promedio")
        if len(df_view) > 0:
            top_bec = (df_view.groupby(["dni_str", "nombres_apellidos", "carrera"])["nota_promedio"]
                       .mean().sort_values(ascending=False).head(10).reset_index())
            top_bec["nota_promedio"] = top_bec["nota_promedio"].round(2)
            top_bec.columns = ["DNI", "Nombre", "Carrera", "Promedio"]
            st.dataframe(top_bec.reset_index(drop=True), use_container_width=True, height=280)

    with col6:
        section_title("Becarios activos sin OM registrado")
        df_sin_om = df_act[~df_act["dni_str"].isin(df_view["dni_str"])].copy()
        st.markdown(f"**{len(df_sin_om):,} becarios** no tienen registro en el semestre seleccionado.")
        cols_sin = ["semestre_registro", "dni", "apellidos_nombres", "carrera", "financiador"]
        st.dataframe(
            df_sin_om[[c for c in cols_sin if c in df_sin_om.columns]].reset_index(drop=True),
            use_container_width=True, height=220,
        )

    section_title("Detalle orden de mérito")
    busqueda = st.text_input("Buscar por nombre o DNI", key="busq_om")
    df_tabla = df_view.copy()
    if busqueda:
        mask = (
            df_tabla["nombres_apellidos"].astype(str).str.contains(busqueda.upper(), na=False) |
            df_tabla["dni_str"].str.contains(busqueda, na=False)
        )
        df_tabla = df_tabla[mask]

    cols_tabla = ["semestre", "dni", "nombres_apellidos", "carrera", "nota_promedio",
                  "orden", "decimo_superior", "quinto_superior", "tercio_superior",
                  "creditos_aprobados", "creditos_desaprobados"]
    st.dataframe(
        df_tabla[[c for c in cols_tabla if c in df_tabla.columns]].reset_index(drop=True),
        use_container_width=True, height=380,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Descargar Excel", df_to_excel_bytes(df_tabla),
                           "orden_merito.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c2:
        st.download_button("Descargar CSV", df_to_csv_bytes(df_tabla),
                           "orden_merito.csv", "text/csv")
