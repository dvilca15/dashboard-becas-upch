import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import df_to_excel_bytes, df_to_csv_bytes
from theme import (
    metric_card, section_title, plotly_layout, plotly_pie_layout, pie_traces_cfg,
    TEAL, EMERALD, DANGER, AMBER,
)


def limpiar_carrera(nombre):
    if not isinstance(nombre, str):
        return nombre
    prefijos = ["CARRERA PROFESIONAL DE ", "CARRERA PROFESIONAL EN ", "CARRERA DE ", "CARRERA EN "]
    for p in prefijos:
        if nombre.upper().startswith(p):
            return nombre[len(p):].strip().title()
    return nombre.strip().title()


def render(df_egr, semestre_sel, carrera_sel, _financiador_sel):
    df_egr = df_egr.copy()
    if "carrera" in df_egr.columns:
        df_egr["carrera"] = df_egr["carrera"].apply(limpiar_carrera)

    df_e = df_egr.copy()
    if semestre_sel != "Todos" and "semestre" in df_e.columns:
        df_e = df_e[df_e["semestre"] == semestre_sel]
    if carrera_sel and "carrera" in df_e.columns:
        df_e = df_e[df_e["carrera"].isin(carrera_sel)]

    total        = len(df_e)
    esperados    = len(df_e[df_e["condicion"].str.upper() == "ESPERADO"]) if "condicion" in df_e.columns else 0
    no_esperados = total - esperados
    semestres_n  = df_e["semestre"].nunique() if "semestre" in df_e.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card(f"{total:,}",        "Total egresados",    accent=TEAL)
    with c2: metric_card(f"{esperados:,}",    "Egreso esperado",    accent=EMERALD)
    with c3: metric_card(f"{no_esperados:,}", "Egreso no esperado", accent=DANGER)
    with c4: metric_card(f"{semestres_n}",    "Semestres",          accent=AMBER)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        section_title("Egresados por semestre")
        if "semestre" in df_e.columns:
            sem_data = df_e.groupby(["semestre", "condicion"]).size().reset_index(name="n")
            sem_data["semestre"] = sem_data["semestre"].astype(str)
            max_val = sem_data["n"].max()
            fig = px.bar(sem_data, x="semestre", y="n", color="condicion",
                         barmode="group",
                         color_discrete_sequence=[EMERALD, DANGER],
                         labels={"semestre": "Semestre", "n": "Cantidad", "condicion": "Condición"},
                         text_auto=True)
            fig.update_traces(textfont=dict(size=10), marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=300,
                xaxis=dict(type="category"),
                yaxis=dict(range=[0, max_val * 1.2]),
            ))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Condición de egreso")
        if "condicion" in df_e.columns:
            cond = df_e["condicion"].value_counts().reset_index()
            cond.columns = ["Condición", "Cantidad"]
            fig = px.pie(cond, values="Cantidad", names="Condición",
                         color_discrete_sequence=[EMERALD, DANGER], hole=0.5)
            fig.update_traces(**pie_traces_cfg())
            fig.update_layout(**plotly_pie_layout(height=300))
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_title("Egresados por carrera (top 10)")
        if "carrera" in df_e.columns:
            carr = df_e["carrera"].value_counts().head(10).reset_index()
            carr.columns = ["Carrera", "Egresados"]
            fig = px.bar(carr, x="Egresados", y="Carrera", orientation="h",
                         color_discrete_sequence=[TEAL], text="Egresados")
            fig.update_traces(textposition="outside", textangle=0,
                              textfont=dict(size=10, family="JetBrains Mono"),
                              marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=320,
                xaxis=dict(range=[0, carr["Egresados"].max() * 1.3], visible=False),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            ))
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_title("Egresados por tipo de beneficio")
        if "tipo_de_beneficio" in df_e.columns:
            ben = df_e["tipo_de_beneficio"].value_counts().reset_index()
            ben.columns = ["Beneficio", "Cantidad"]
            fig = px.bar(ben, x="Cantidad", y="Beneficio", orientation="h",
                         color_discrete_sequence=[AMBER], text="Cantidad")
            fig.update_traces(textposition="outside", textangle=0,
                              textfont=dict(size=10, family="JetBrains Mono"),
                              marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=320,
                xaxis=dict(range=[0, ben["Cantidad"].max() * 1.3], visible=False),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            ))
            st.plotly_chart(fig, use_container_width=True)

    section_title("Detalle de egresados")
    busqueda = st.text_input("Buscar por nombre o DNI")
    df_tabla = df_e.copy()
    if busqueda:
        nombre_col = "apellidos_y_nombres" if "apellidos_y_nombres" in df_tabla.columns else "apellidos_nombres"
        if nombre_col in df_tabla.columns:
            mask = (
                df_tabla[nombre_col].astype(str).str.contains(busqueda.upper(), na=False) |
                df_tabla["dni"].astype(str).str.contains(busqueda, na=False)
            )
            df_tabla = df_tabla[mask]

    cols_tabla = ["semestre", "dni", "apellidos_y_nombres", "carrera", "tipo_de_beneficio",
                  "modalidad", "convocatoria", "ciclo", "condicion", "matricula"]
    st.dataframe(
        df_tabla[[c for c in cols_tabla if c in df_tabla.columns]].reset_index(drop=True),
        use_container_width=True, height=350,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Descargar Excel", df_to_excel_bytes(df_tabla),
                           "egresados.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c2:
        st.download_button("Descargar CSV", df_to_csv_bytes(df_tabla),
                           "egresados.csv", "text/csv")
