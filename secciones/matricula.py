import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import df_to_excel_bytes, df_to_csv_bytes
from theme import (
    metric_card, section_title, plotly_layout, plotly_pie_layout, pie_traces_cfg,
    TEAL, EMERALD, DANGER, AMBER, PALETTE,
)


def render(df_bec, _df_mat, semestre_sel, carrera_sel, financiador_sel):
    df_activos = df_bec[df_bec["estado_beneficiario"] == "ACTIVO"].copy()
    if semestre_sel != "Todos":
        df_activos = df_activos[df_activos["semestre_registro"] == semestre_sel]
    if carrera_sel:
        df_activos = df_activos[df_activos["carrera"].isin(carrera_sel)]
    if financiador_sel:
        df_activos = df_activos[df_activos["financiador"].isin(financiador_sel)]

    total_activos = len(df_activos)
    si_mat = len(df_activos[df_activos["matriculado"] == "MATRICULADO"])
    no_mat = total_activos - si_mat
    pct    = f"{(si_mat/total_activos*100):.1f}%" if total_activos > 0 else "0%"

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card(f"{total_activos:,}", "Becarios activos", accent=TEAL)
    with c2: metric_card(
        f"{si_mat:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {pct}</span>",
        "Matriculados", accent=EMERALD,
    )
    with c3: metric_card(f"{no_mat:,}", "No matriculados", accent=DANGER)
    with c4:
        sem_label = semestre_sel
        metric_card(sem_label, "Semestre", accent=AMBER)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        section_title("Matriculados vs No matriculados")
        pie_data = pd.DataFrame({
            "Estado": ["Matriculados", "No matriculados"],
            "Cantidad": [si_mat, no_mat],
        })
        fig = px.pie(pie_data, values="Cantidad", names="Estado",
                     color_discrete_sequence=[EMERALD, DANGER], hole=0.5)
        fig.update_traces(**pie_traces_cfg())
        fig.update_layout(**plotly_pie_layout(height=300))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Matriculados vs No matriculados por semestre")
        semestres_todos = sorted(df_bec["semestre_registro"].dropna().unique().tolist(), reverse=True)
        comp = []
        for sem in semestres_todos:
            df_sem = df_bec[(df_bec["estado_beneficiario"] == "ACTIVO") &
                            (df_bec["semestre_registro"] == sem)]
            si  = len(df_sem[df_sem["matriculado"] == "MATRICULADO"])
            no  = len(df_sem) - si
            comp.append({"Semestre": str(sem), "Matriculados": si, "No matriculados": no})
        df_comp = pd.DataFrame(comp)
        max_val = df_comp[["Matriculados", "No matriculados"]].max().max()
        fig = go.Figure()
        fig.add_bar(x=df_comp["Semestre"], y=df_comp["Matriculados"], name="Matriculados",
                    marker_color=EMERALD, text=df_comp["Matriculados"], textposition="outside",
                    textfont=dict(size=10, family="JetBrains Mono"))
        fig.add_bar(x=df_comp["Semestre"], y=df_comp["No matriculados"], name="No matriculados",
                    marker_color=DANGER, text=df_comp["No matriculados"], textposition="outside",
                    textfont=dict(size=10, family="JetBrains Mono"))
        fig.update_layout(**plotly_layout(
            barmode="group", height=300,
            xaxis=dict(type="category"),
            yaxis=dict(range=[0, max_val * 1.2]),
        ))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        section_title("Matriculados por carrera (top 10)")
        mat_carrera = (df_activos[df_activos["matriculado"] == "MATRICULADO"]
                       .groupby("carrera").size().sort_values(ascending=False)
                       .head(10).reset_index())
        mat_carrera.columns = ["Carrera", "Matriculados"]
        fig = px.bar(mat_carrera, x="Matriculados", y="Carrera", orientation="h",
                     color_discrete_sequence=[TEAL], text="Matriculados")
        fig.update_traces(textposition="outside", textangle=0,
                          textfont=dict(size=10, family="JetBrains Mono"),
                          marker_line_width=0)
        fig.update_layout(**plotly_layout(
            height=320,
            xaxis=dict(range=[0, mat_carrera["Matriculados"].max() * 1.3], visible=False),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_title("Detalle estado de matrícula")
        est_mat = df_activos["matriculado"].value_counts().reset_index()
        est_mat.columns = ["Estado", "Cantidad"]
        fig = px.bar(est_mat, x="Cantidad", y="Estado", orientation="h",
                     color_discrete_sequence=PALETTE, text="Cantidad")
        fig.update_traces(textposition="outside", textangle=0,
                          textfont=dict(size=10, family="JetBrains Mono"))
        fig.update_layout(**plotly_layout(
            height=320,
            xaxis=dict(range=[0, est_mat["Cantidad"].max() * 1.3], visible=False),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        ))
        st.plotly_chart(fig, use_container_width=True)

    cols_tabla = ["semestre_registro", "dni", "apellidos_nombres", "carrera",
                  "financiador", "beneficio", "matriculado"]

    # ── No matriculados ──────────────────────────────────────────────────────
    section_title("Becarios activos NO matriculados")
    df_no_mat = df_activos[df_activos["matriculado"] != "MATRICULADO"].copy()

    busqueda = st.text_input("Buscar por nombre o DNI", key="busq_no_mat")
    if busqueda:
        mask = (
            df_no_mat["apellidos_nombres"].astype(str).str.contains(busqueda.upper(), na=False) |
            df_no_mat["dni"].astype(str).str.contains(busqueda, na=False)
        )
        df_no_mat = df_no_mat[mask]

    st.dataframe(df_no_mat[[c for c in cols_tabla if c in df_no_mat.columns]].reset_index(drop=True),
                 use_container_width=True, height=350)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Descargar Excel", df_to_excel_bytes(df_no_mat),
                           "no_matriculados.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="dl_excel_no_mat")
    with c2:
        st.download_button("Descargar CSV", df_to_csv_bytes(df_no_mat),
                           "no_matriculados.csv", "text/csv", key="dl_csv_no_mat")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Matriculados ─────────────────────────────────────────────────────────
    section_title("Becarios activos MATRICULADOS")
    df_mat_tab = df_activos[df_activos["matriculado"] == "MATRICULADO"].copy()

    busqueda2 = st.text_input("Buscar por nombre o DNI", key="busq_mat")
    if busqueda2:
        mask2 = (
            df_mat_tab["apellidos_nombres"].astype(str).str.contains(busqueda2.upper(), na=False) |
            df_mat_tab["dni"].astype(str).str.contains(busqueda2, na=False)
        )
        df_mat_tab = df_mat_tab[mask2]

    st.dataframe(df_mat_tab[[c for c in cols_tabla if c in df_mat_tab.columns]].reset_index(drop=True),
                 use_container_width=True, height=350)

    c3, c4 = st.columns(2)
    with c3:
        st.download_button("Descargar Excel", df_to_excel_bytes(df_mat_tab),
                           "matriculados.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="dl_excel_mat")
    with c4:
        st.download_button("Descargar CSV", df_to_csv_bytes(df_mat_tab),
                           "matriculados.csv", "text/csv", key="dl_csv_mat")
