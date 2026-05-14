import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import df_to_excel_bytes, df_to_csv_bytes
from theme import (
    metric_card, section_title, plotly_layout, plotly_pie_layout, pie_traces_cfg, group_tail,
    TEAL, EMERALD, DANGER, AMBER, VIOLET, PALETTE,
)


def render(df_bec, semestre_sel, carrera_sel, financiador_sel):
    SEMESTRES = sorted(df_bec["semestre_registro"].dropna().unique().tolist(), reverse=True)

    df_b = df_bec.copy()
    if semestre_sel != "Todos":
        df_b = df_b[df_b["semestre_registro"] == semestre_sel]
    if carrera_sel:
        df_b = df_b[df_b["carrera"].isin(carrera_sel)]
    if financiador_sel:
        df_b = df_b[df_b["financiador"].isin(financiador_sel)]

    total      = len(df_b)
    activos    = len(df_b[df_b["estado_beneficiario"] == "ACTIVO"])
    inactivos  = total - activos
    carreras_n = df_b["carrera"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card(f"{total:,}",      "Total becarios",   accent=TEAL)
    with c2: metric_card(f"{activos:,}",    "Activos",          accent=EMERALD)
    with c3: metric_card(f"{inactivos:,}",  "Inactivos",        accent=DANGER)
    with c4: metric_card(f"{carreras_n:,}", "Carreras",         accent=VIOLET)

    st.markdown("<br>", unsafe_allow_html=True)

    # Fila 1: activos por semestre + estado
    col1, col2 = st.columns(2)

    with col1:
        section_title("Becarios activos por semestre")
        comp = []
        for sem in SEMESTRES:
            act = len(df_bec[(df_bec["semestre_registro"] == sem) & (df_bec["estado_beneficiario"] == "ACTIVO")])
            ina = len(df_bec[(df_bec["semestre_registro"] == sem) & (df_bec["estado_beneficiario"] != "ACTIVO")])
            comp.append({"Semestre": str(sem), "Activos": act, "Inactivos": ina})
        df_comp = pd.DataFrame(comp)
        max_val = df_comp[["Activos", "Inactivos"]].max().max()
        fig = go.Figure()
        fig.add_bar(x=df_comp["Semestre"], y=df_comp["Activos"], name="Activos",
                    marker_color=EMERALD, text=df_comp["Activos"], textposition="outside",
                    textfont=dict(size=10, family="JetBrains Mono"))
        fig.add_bar(x=df_comp["Semestre"], y=df_comp["Inactivos"], name="Inactivos",
                    marker_color=DANGER, text=df_comp["Inactivos"], textposition="outside",
                    textfont=dict(size=10, family="JetBrains Mono"))
        fig.update_layout(**plotly_layout(
            barmode="group", height=300,
            xaxis=dict(type="category"),
            yaxis=dict(range=[0, max_val * 1.2]),
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Estado de becarios")
        estado_data = df_b["estado_beneficiario"].value_counts().reset_index()
        estado_data.columns = ["Estado", "Cantidad"]
        fig = px.pie(estado_data, values="Cantidad", names="Estado",
                     color_discrete_sequence=[EMERALD, DANGER, AMBER], hole=0.5)
        fig.update_traces(**pie_traces_cfg())
        fig.update_layout(**plotly_pie_layout(height=300))
        st.plotly_chart(fig, use_container_width=True)

    # Fila 2: top carreras + por financiador
    col3, col4 = st.columns(2)

    with col3:
        section_title("Top 10 carreras con más becarios")
        top_carr = df_b["carrera"].value_counts().head(10).reset_index()
        top_carr.columns = ["Carrera", "Becarios"]
        fig = px.bar(top_carr, x="Becarios", y="Carrera", orientation="h",
                     color_discrete_sequence=[TEAL], text="Becarios")
        fig.update_traces(textposition="outside", textangle=0,
                          textfont=dict(size=10, family="JetBrains Mono"),
                          marker_line_width=0)
        fig.update_layout(**plotly_layout(
            height=300,
            xaxis=dict(range=[0, top_carr["Becarios"].max() * 1.3], visible=False),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        section_title("Becarios por financiador")
        fin_series = df_b["financiador"].value_counts()
        priority = ["PRONABEC", "UPCH"]
        p_labels, p_values = [], []
        otros = 0
        for fin, cnt in fin_series.items():
            if fin in priority:
                p_labels.append(fin)
                p_values.append(cnt)
            else:
                otros += cnt
        if otros > 0:
            p_labels.append("Otros")
            p_values.append(otros)
        fig = px.pie(names=p_labels, values=p_values,
                     color_discrete_sequence=PALETTE, hole=0.45)
        fig.update_traces(**pie_traces_cfg())
        fig.update_layout(**plotly_pie_layout(height=300))
        st.plotly_chart(fig, use_container_width=True)

    # Fila 3: por sexo + por tipo de beneficio
    col5, col6 = st.columns(2)

    with col5:
        section_title("Activos por sexo y semestre")
        sexo_sem = (df_bec[df_bec["estado_beneficiario"] == "ACTIVO"]
                    .groupby(["semestre_registro", "sexo"]).size().reset_index(name="n"))
        sexo_sem["semestre_registro"] = sexo_sem["semestre_registro"].astype(str)
        fig = px.bar(sexo_sem, x="semestre_registro", y="n", color="sexo",
                     barmode="group",
                     color_discrete_sequence=[TEAL, VIOLET],
                     labels={"semestre_registro": "Semestre", "n": "Cantidad", "sexo": "Sexo"},
                     text_auto=True)
        fig.update_traces(textfont=dict(size=10), marker_line_width=0)
        fig.update_layout(**plotly_layout(height=280, xaxis=dict(type="category")))
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        section_title("Top tipos de beneficio")
        beneficio = df_b["beneficio"].value_counts().head(8).reset_index()
        beneficio.columns = ["Beneficio", "Cantidad"]
        fig = px.bar(beneficio, x="Cantidad", y="Beneficio", orientation="h",
                     color_discrete_sequence=[AMBER], text="Cantidad")
        fig.update_traces(textposition="outside", textangle=0,
                          textfont=dict(size=10, family="JetBrains Mono"),
                          marker_line_width=0)
        fig.update_layout(**plotly_layout(
            height=280,
            xaxis=dict(range=[0, beneficio["Cantidad"].max() * 1.3], visible=False),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
        ))
        st.plotly_chart(fig, use_container_width=True)
