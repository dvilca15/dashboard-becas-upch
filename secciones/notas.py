import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import df_to_excel_bytes, df_to_csv_bytes
from theme import (
    metric_card, section_title, plotly_layout,
    TEAL, EMERALD, DANGER, AMBER, VIOLET,
)

SEMESTRE_A_PERIODO = {
    "2025-1": 20251,
    "2025-2": 20252,
    "2026-1": 20261,
}


def limpiar_carrera(nombre):
    if not isinstance(nombre, str):
        return nombre
    prefijos = ["CARRERA PROFESIONAL DE ", "CARRERA PROFESIONAL EN ", "CARRERA DE ", "CARRERA EN "]
    for p in prefijos:
        if nombre.upper().startswith(p):
            return nombre[len(p):].strip().title()
    return nombre.strip().title()


def render(df_bec, df_not, semestre_sel, carrera_sel, financiador_sel):
    df_not = df_not.copy()
    df_not["nombre_carrera"] = df_not["nombre_carrera"].apply(limpiar_carrera)

    df_act = df_bec[df_bec["estado_beneficiario"] == "ACTIVO"].copy()
    if semestre_sel != "Todos":
        df_act = df_act[df_act["semestre_registro"] == semestre_sel]
    if carrera_sel:
        df_act = df_act[df_act["carrera"].isin(carrera_sel)]
    if financiador_sel:
        df_act = df_act[df_act["financiador"].isin(financiador_sel)]

    dnis_activos = set(df_act["dni"].unique())
    df_n = df_not[df_not["dni"].isin(dnis_activos)].copy()

    periodos_disp = sorted(df_n["periodo_academico"].dropna().unique().tolist())
    periodos_disp_str = [str(int(p)) for p in periodos_disp]
    periodo_sel = st.selectbox(
        "Ver notas del periodo académico",
        ["Todos"] + periodos_disp_str,
        key="sel_periodo_notas",
        help="Filtra los gráficos por periodo.",
    )

    if periodo_sel != "Todos":
        df_n = df_n[df_n["periodo_academico"] == int(periodo_sel)]

    df_des = df_n[df_n["condicion"].str.upper() == "DESAPROBADO"].copy()
    df_des = df_des[~df_des["nombre_asignatura"].str.upper().str.contains("ACTIVIDAD COMPLEMENTARIA", na=False)]

    total_notas       = len(df_n)
    total_des         = len(df_des)
    becarios_con_des  = df_des["dni"].nunique()
    total_activos     = len(df_act)
    pct_des           = f"{(becarios_con_des/total_activos*100):.1f}%" if total_activos > 0 else "0%"
    becarios_con_nota = df_n["dni"].nunique()
    pct_con_nota      = f"{(becarios_con_nota/total_activos*100):.1f}%" if total_activos > 0 else "0%"

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_card(f"{total_activos:,}", "Becarios activos", accent=TEAL)
    with c2: metric_card(
        f"{becarios_con_nota:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {pct_con_nota}</span>",
        "Con nota", accent=EMERALD,
    )
    with c3: metric_card(f"{total_notas:,}", "Total registros", accent=TEAL)
    with c4: metric_card(f"{total_des:,}", "Cursos desaprobados", accent=DANGER)
    with c5: metric_card(
        f"{becarios_con_des:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {pct_des}</span>",
        "Becarios con desap.", accent=AMBER,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        section_title("Top 15 cursos más desaprobados")
        if len(df_des) > 0:
            top_cur = df_des["nombre_asignatura"].value_counts().head(15).reset_index()
            top_cur.columns = ["Curso", "Desaprobados"]
            fig = px.bar(top_cur, x="Desaprobados", y="Curso", orientation="h",
                         color_discrete_sequence=[DANGER], text="Desaprobados")
            fig.update_traces(textposition="outside", textangle=0,
                              textfont=dict(size=10, family="JetBrains Mono"),
                              marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=420,
                xaxis=dict(range=[0, top_cur["Desaprobados"].max() * 1.3], visible=False),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            ))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay desaprobados para el filtro seleccionado.")

    with col2:
        section_title("Desaprobados por periodo académico")
        if len(df_des) > 0:
            per_data = df_des.groupby("periodo_academico").agg(
                Desaprobados=("dni", "count"),
                Becarios=("dni", "nunique"),
            ).reset_index()
            per_data["periodo_academico"] = per_data["periodo_academico"].astype(str)
            fig = go.Figure()
            fig.add_bar(x=per_data["periodo_academico"], y=per_data["Desaprobados"],
                        name="Cursos desaprobados", marker_color=DANGER,
                        text=per_data["Desaprobados"], textposition="outside",
                        textfont=dict(size=10, family="JetBrains Mono"))
            fig.add_bar(x=per_data["periodo_academico"], y=per_data["Becarios"],
                        name="Becarios afectados", marker_color=AMBER,
                        text=per_data["Becarios"], textposition="outside",
                        textfont=dict(size=10, family="JetBrains Mono"))
            max_val = per_data[["Desaprobados", "Becarios"]].max().max()
            fig.update_layout(**plotly_layout(
                barmode="group", height=420,
                xaxis=dict(type="category"),
                yaxis=dict(range=[0, max_val * 1.2]),
            ))
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_title("Desaprobados por carrera (top 10)")
        if len(df_des) > 0:
            des_carr = df_des["nombre_carrera"].value_counts().head(10).reset_index()
            des_carr.columns = ["Carrera", "Desaprobados"]
            fig = px.bar(des_carr, x="Desaprobados", y="Carrera", orientation="h",
                         color_discrete_sequence=[TEAL], text="Desaprobados")
            fig.update_traces(textposition="outside", textangle=0,
                              textfont=dict(size=10, family="JetBrains Mono"),
                              marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=320,
                xaxis=dict(range=[0, des_carr["Desaprobados"].max() * 1.3], visible=False),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            ))
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_title("Desaprobados por ciclo del estudiante")
        if len(df_des) > 0:
            des_ciclo = df_des["ciclo_estudiante"].value_counts().sort_index().reset_index()
            des_ciclo.columns = ["Ciclo", "Desaprobados"]
            des_ciclo["Ciclo"] = des_ciclo["Ciclo"].astype(str)
            fig = px.bar(des_ciclo, x="Ciclo", y="Desaprobados",
                         color_discrete_sequence=[AMBER], text_auto=True)
            fig.update_traces(textfont=dict(size=10), marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=320, showlegend=False, xaxis=dict(type="category"),
            ))
            st.plotly_chart(fig, use_container_width=True)

    section_title("Top cursos desaprobados por carrera")
    carreras_disp = sorted(df_des["nombre_carrera"].dropna().unique().tolist())
    carrera_nota = st.selectbox("Selecciona una carrera", ["Todas"] + carreras_disp, key="sel_carrera_nota")
    df_des_carr = df_des if carrera_nota == "Todas" else df_des[df_des["nombre_carrera"] == carrera_nota]
    if len(df_des_carr) > 0:
        top_carr_cur = df_des_carr["nombre_asignatura"].value_counts().head(10).reset_index()
        top_carr_cur.columns = ["Curso", "Desaprobados"]
        fig = px.bar(top_carr_cur, x="Desaprobados", y="Curso", orientation="h",
                     color_discrete_sequence=[VIOLET], text="Desaprobados")
        fig.update_traces(textposition="outside", textangle=0,
                          textfont=dict(size=10, family="JetBrains Mono"),
                          marker_line_width=0)
        fig.update_layout(**plotly_layout(
            height=340,
            xaxis=dict(range=[0, top_carr_cur["Desaprobados"].max() * 1.3], visible=False),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        ))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay desaprobados para esta carrera.")

    section_title("Detalle de cursos desaprobados")
    busqueda = st.text_input("Buscar por nombre, DNI o curso", key="busq_notas")
    df_tabla = df_des.copy()
    if busqueda:
        mask = (
            df_tabla["apellidos_nombre"].astype(str).str.contains(busqueda.upper(), na=False) |
            df_tabla["dni"].astype(str).str.contains(busqueda, na=False) |
            df_tabla["nombre_asignatura"].astype(str).str.contains(busqueda.upper(), na=False)
        )
        df_tabla = df_tabla[mask]

    cols_tabla = ["periodo_academico", "dni", "apellidos_nombre", "nombre_carrera",
                  "ciclo_estudiante", "nombre_asignatura", "promedio_curso", "condicion"]
    st.dataframe(
        df_tabla[[c for c in cols_tabla if c in df_tabla.columns]].reset_index(drop=True),
        use_container_width=True, height=350,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Descargar Excel", df_to_excel_bytes(df_tabla),
                           "desaprobados.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c2:
        st.download_button("Descargar CSV", df_to_csv_bytes(df_tabla),
                           "desaprobados.csv", "text/csv")
