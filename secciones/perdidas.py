import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import df_to_excel_bytes, df_to_csv_bytes
from theme import (
    metric_card, section_title, plotly_layout, plotly_pie_layout, pie_traces_cfg,
    TEAL, DANGER, AMBER, ORANGE, PALETTE,
)

SITUACIONES_INTERES = ["CAMBIO DE IES", "RENUNCIA", "ABANDONO"]


def render(df_bec, df_per, semestre_sel, carrera_sel, financiador_sel):
    SEMESTRES = sorted(df_bec["semestre_registro"].dropna().unique().tolist(), reverse=True)

    df_act = df_bec[df_bec["estado_beneficiario"] == "ACTIVO"].copy()
    if semestre_sel != "Todos":
        df_act = df_act[df_act["semestre_registro"] == semestre_sel]
    if carrera_sel:
        df_act = df_act[df_act["carrera"].isin(carrera_sel)]
    if financiador_sel:
        df_act = df_act[df_act["financiador"].isin(financiador_sel)]

    df_inac = df_bec[df_bec["estado_beneficiario"] == "INACTIVO"].copy()
    if semestre_sel != "Todos":
        df_inac = df_inac[df_inac["semestre_registro"] == semestre_sel]
    if carrera_sel:
        df_inac = df_inac[df_inac["carrera"].isin(carrera_sel)]
    if financiador_sel:
        df_inac = df_inac[df_inac["financiador"].isin(financiador_sel)]

    df_p = df_per.copy()
    if semestre_sel != "Todos":
        df_p = df_p[df_p["semestre"] == semestre_sel]

    activos    = len(df_act)
    total_per  = len(df_p)
    bajo_rend  = len(df_p[df_p["condicion"].str.contains("BAJO RENDIMIENTO", na=False)])
    desaprobo  = len(df_p[df_p["condicion"].str.contains("DESAPROBO", na=False)])
    tasa_des   = f"{(desaprobo/activos*100):.1f}% de activos" if activos > 0 else "0%"
    tasa_baj   = f"{(bajo_rend/activos*100):.1f}% de activos" if activos > 0 else "0%"

    df_sit       = df_inac[df_inac["situacion_beneficiario"].isin(SITUACIONES_INTERES)]
    total_inac   = len(df_inac)
    cambio_ies   = len(df_inac[df_inac["situacion_beneficiario"] == "CAMBIO DE IES"])
    renuncia     = len(df_inac[df_inac["situacion_beneficiario"] == "RENUNCIA"])
    abandono     = len(df_inac[df_inac["situacion_beneficiario"] == "ABANDONO"])
    tasa_cambio  = f"{(cambio_ies/activos*100):.1f}%" if activos > 0 else "0%"
    tasa_renuncia = f"{(renuncia/activos*100):.1f}%" if activos > 0 else "0%"
    tasa_abandono = f"{(abandono/activos*100):.1f}%" if activos > 0 else "0%"

    # ── Sección 1: Pérdidas por rendimiento ──────────────────────────────────
    st.markdown("### Pérdidas de beca por rendimiento")
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card(f"{activos:,}", "Becarios activos", accent=TEAL)
    with c2: metric_card(f"{total_per:,}", "Total pérdidas", accent=DANGER)
    with c3: metric_card(
        f"{desaprobo:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {tasa_des}</span>",
        "Desaprobó todos los cursos", accent=DANGER,
    )
    with c4: metric_card(
        f"{bajo_rend:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {tasa_baj}</span>",
        "Separado por bajo rendimiento", accent=AMBER,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        section_title("Activos vs Pérdidas por semestre")
        resumen = []
        for sem in SEMESTRES:
            act = len(df_bec[(df_bec["semestre_registro"] == sem) & (df_bec["estado_beneficiario"] == "ACTIVO")])
            per = len(df_per[df_per["semestre"] == sem])
            resumen.append({"Semestre": str(sem), "Activos": act, "Perdidas": per})
        df_res = pd.DataFrame(resumen)
        max_val = df_res[["Activos", "Perdidas"]].max().max()
        fig = go.Figure()
        fig.add_bar(x=df_res["Semestre"], y=df_res["Activos"], name="Activos",
                    marker_color=TEAL, text=df_res["Activos"], textposition="outside",
                    textfont=dict(size=10, family="JetBrains Mono"))
        fig.add_bar(x=df_res["Semestre"], y=df_res["Perdidas"], name="Pérdidas",
                    marker_color=DANGER, text=df_res["Perdidas"], textposition="outside",
                    textfont=dict(size=10, family="JetBrains Mono"))
        fig.update_layout(**plotly_layout(
            barmode="group", height=300,
            xaxis=dict(type="category"),
            yaxis=dict(range=[0, max_val * 1.2]),
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Pérdidas por condición")
        if len(df_p) > 0:
            per_cond = df_p["condicion"].value_counts().reset_index()
            per_cond.columns = ["Condición", "Cantidad"]
            fig = px.pie(per_cond, values="Cantidad", names="Condición",
                         color_discrete_sequence=PALETTE, hole=0.45)
            fig.update_traces(**pie_traces_cfg())
            fig.update_layout(**plotly_pie_layout(height=300))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay pérdidas para el filtro seleccionado.")

    col3, col4 = st.columns(2)
    with col3:
        section_title("Pérdidas por carrera")
        if len(df_p) > 0:
            per_carrera = df_p["nombre_carrera"].value_counts().reset_index()
            per_carrera.columns = ["Carrera", "Pérdidas"]
            fig = px.bar(per_carrera, x="Pérdidas", y="Carrera", orientation="h",
                         color_discrete_sequence=[DANGER], text="Pérdidas")
            fig.update_traces(textposition="outside", textangle=0,
                              textfont=dict(size=10, family="JetBrains Mono"),
                              marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=320,
                xaxis=dict(range=[0, per_carrera["Pérdidas"].max() * 1.3], visible=False),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            ))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay pérdidas para el filtro seleccionado.")

    with col4:
        section_title("Pérdidas por tipo de beneficio")
        if len(df_p) > 0:
            per_ben = df_p["tipo_de_beneficio"].value_counts().reset_index()
            per_ben.columns = ["Beneficio", "Cantidad"]
            fig = px.bar(per_ben, x="Cantidad", y="Beneficio", orientation="h",
                         color_discrete_sequence=[AMBER], text="Cantidad")
            fig.update_traces(textposition="outside", textangle=0,
                              textfont=dict(size=10, family="JetBrains Mono"),
                              marker_line_width=0)
            fig.update_layout(**plotly_layout(
                height=320,
                xaxis=dict(range=[0, per_ben["Cantidad"].max() * 1.3], visible=False),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            ))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay pérdidas para el filtro seleccionado.")

    section_title("Detalle de pérdidas de beca")
    busqueda1 = st.text_input("Buscar por nombre o DNI", key="busq_perdidas")
    df_tabla = df_p.copy()
    if busqueda1:
        mask = (
            df_tabla["apellidos_nombre"].astype(str).str.contains(busqueda1.upper(), na=False) |
            df_tabla["dni"].astype(str).str.contains(busqueda1, na=False)
        )
        df_tabla = df_tabla[mask]
    cols_tabla = ["semestre", "dni", "apellidos_nombre", "nombre_carrera",
                  "tipo_de_beneficio", "condicion", "cursos_desaprobados_en_semestre"]
    st.dataframe(df_tabla[[c for c in cols_tabla if c in df_tabla.columns]].reset_index(drop=True),
                 use_container_width=True, height=300)
    ca, cb = st.columns(2)
    with ca:
        st.download_button("Descargar Excel", df_to_excel_bytes(df_tabla),
                           "perdidas_beca.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with cb:
        st.download_button("Descargar CSV", df_to_csv_bytes(df_tabla),
                           "perdidas_beca.csv", "text/csv")

    st.markdown("---")

    # ── Sección 2: Inactivos por situación ───────────────────────────────────
    st.markdown("### Inactivos — Cambio de IES, Renuncia y Abandono")

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card(f"{total_inac:,}", "Total inactivos", accent=DANGER)
    with c2: metric_card(
        f"{cambio_ies:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {tasa_cambio}</span>",
        "Cambio de IES", accent=DANGER,
    )
    with c3: metric_card(
        f"{renuncia:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {tasa_renuncia}</span>",
        "Renuncia", accent=AMBER,
    )
    with c4: metric_card(
        f"{abandono:,} <span style='font-size:.9rem;color:#78716C;font-weight:400'>· {tasa_abandono}</span>",
        "Abandono", accent=AMBER,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col5, col6 = st.columns(2)

    with col5:
        section_title("Cambio IES / Renuncia / Abandono por semestre")
        comp_sit = []
        for sem in SEMESTRES:
            df_sem_inac = df_bec[
                (df_bec["estado_beneficiario"] == "INACTIVO") &
                (df_bec["semestre_registro"] == sem) &
                (df_bec["situacion_beneficiario"].isin(SITUACIONES_INTERES))
            ]
            act_sem = len(df_bec[(df_bec["estado_beneficiario"] == "ACTIVO") &
                                 (df_bec["semestre_registro"] == sem)])
            for sit in SITUACIONES_INTERES:
                n = len(df_sem_inac[df_sem_inac["situacion_beneficiario"] == sit])
                tasa = f"{(n/act_sem*100):.1f}%" if act_sem > 0 else "0%"
                comp_sit.append({"Semestre": str(sem), "Situación": sit, "Cantidad": n, "Tasa": tasa})
        df_comp_sit = pd.DataFrame(comp_sit)
        fig = px.bar(df_comp_sit, x="Semestre", y="Cantidad", color="Situación",
                     barmode="group",
                     color_discrete_sequence=[DANGER, AMBER, ORANGE],
                     text="Cantidad")
        fig.update_traces(textposition="outside",
                          textfont=dict(size=10, family="JetBrains Mono"),
                          marker_line_width=0)
        max_val2 = df_comp_sit["Cantidad"].max()
        fig.update_layout(**plotly_layout(
            height=300,
            xaxis=dict(type="category"),
            yaxis=dict(range=[0, max_val2 * 1.3]),
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        section_title("Distribución de situaciones de interés")
        if len(df_sit) > 0:
            sit_dist = df_sit["situacion_beneficiario"].value_counts().reset_index()
            sit_dist.columns = ["Situación", "Cantidad"]
            fig = px.pie(sit_dist, values="Cantidad", names="Situación",
                         color_discrete_sequence=[DANGER, AMBER, ORANGE], hole=0.45)
            fig.update_traces(**pie_traces_cfg())
            fig.update_layout(**plotly_pie_layout(height=300))
            st.plotly_chart(fig, use_container_width=True)

    section_title("Tasa sobre activos por semestre")
    tasa_rows = []
    for sem in SEMESTRES:
        act_sem = len(df_bec[(df_bec["estado_beneficiario"] == "ACTIVO") & (df_bec["semestre_registro"] == sem)])
        df_sem_inac = df_bec[(df_bec["estado_beneficiario"] == "INACTIVO") & (df_bec["semestre_registro"] == sem)]
        for sit in SITUACIONES_INTERES:
            n = len(df_sem_inac[df_sem_inac["situacion_beneficiario"] == sit])
            tasa = f"{(n/act_sem*100):.2f}%" if act_sem > 0 else "0%"
            tasa_rows.append({"Semestre": sem, "Situación": sit, "Cantidad": n,
                               "Activos en semestre": act_sem, "Tasa": tasa})
    df_tasa = pd.DataFrame(tasa_rows)
    st.dataframe(df_tasa.reset_index(drop=True), use_container_width=True, height=200)

    section_title("Detalle inactivos (Cambio IES / Renuncia / Abandono)")
    busqueda2 = st.text_input("Buscar por nombre o DNI", key="busq_inactivos")
    df_sit_tabla = df_sit.copy()
    if busqueda2:
        mask2 = (
            df_sit_tabla["apellidos_nombres"].astype(str).str.contains(busqueda2.upper(), na=False) |
            df_sit_tabla["dni"].astype(str).str.contains(busqueda2, na=False)
        )
        df_sit_tabla = df_sit_tabla[mask2]

    cols_sit = ["semestre_registro", "dni", "apellidos_nombres", "carrera",
                "financiador", "situacion_beneficiario", "condicion_beneficiario"]
    st.dataframe(df_sit_tabla[[c for c in cols_sit if c in df_sit_tabla.columns]].reset_index(drop=True),
                 use_container_width=True, height=320)

    ca2, cb2 = st.columns(2)
    with ca2:
        st.download_button("Descargar Excel", df_to_excel_bytes(df_sit_tabla),
                           "inactivos_situacion.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           key="dl_excel_inac")
    with cb2:
        st.download_button("Descargar CSV", df_to_csv_bytes(df_sit_tabla),
                           "inactivos_situacion.csv", "text/csv", key="dl_csv_inac")
