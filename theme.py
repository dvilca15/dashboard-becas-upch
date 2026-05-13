"""Design system — Becas UPCH Operator Dashboard."""
import streamlit as st

# ── Color palette ──────────────────────────────────────────────────────────────
TEAL    = "#2D7D8E"   # --accent  (deep teal)
EMERALD = "#16A34A"   # --positive
AMBER   = "#D97706"   # --warning
DANGER  = "#DC2626"   # --danger
VIOLET  = "#7C3AED"   # --violet
INFO    = "#3B82F6"   # --info
ORANGE  = "#EA580C"   # --orange

PALETTE = [TEAL, EMERALD, AMBER, VIOLET, INFO, DANGER, ORANGE]

# Backward-compat aliases (old sections used COLOR_* names)
COLOR_BLUE   = TEAL
COLOR_GREEN  = EMERALD
COLOR_YELLOW = AMBER
COLOR_RED    = DANGER
COLOR_PURPLE = VIOLET
COLOR_ORANGE = ORANGE


def metric_card(value, label, accent=TEAL, delta=None, delta_dir=None):
    """KPI card with left accent bar — operator dashboard style."""
    delta_html = ""
    if delta:
        cls = f"kpi-delta {delta_dir or ''}"
        delta_html = f'<div class="{cls}">{delta}</div>'
    st.markdown(f"""
    <div class="kpi-card" style="--kpi-accent:{accent};">
        <div class="kpi-accent-bar"></div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_title(text):
    st.markdown(f'<p class="section-title">{text}</p>', unsafe_allow_html=True)


def plotly_pie_layout(height=300, **kwargs):
    """Layout for donut/pie charts — clean, no label clutter."""
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Plus Jakarta Sans', sans-serif", color="#44403C", size=11),
        height=height,
        margin=dict(t=10, b=48, l=10, r=10),
        legend=dict(
            orientation="h",
            y=-0.06,
            yanchor="top",
            x=0.5,
            xanchor="center",
            font=dict(size=10.5, family="'Plus Jakarta Sans', sans-serif"),
            itemsizing="constant",
            tracegroupgap=2,
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
    )
    base.update(kwargs)
    return base


def pie_traces_cfg():
    """Standard update_traces kwargs for donut/pie — percent inside, no outside clutter."""
    return dict(
        textposition="inside",
        textinfo="percent",
        textfont=dict(size=10.5, color="white", family="'JetBrains Mono', monospace"),
        insidetextorientation="radial",
        hovertemplate="%{label}<br><b>%{value:,}</b> · %{percent}<extra></extra>",
    )


def group_tail(series, top_n=6, other_label="Otros"):
    """Keep top_n categories, collapse the rest into 'Otros'. Returns (labels, values)."""
    top = series.nlargest(top_n)
    tail_sum = series.sum() - top.sum()
    if tail_sum > 0:
        import pandas as pd
        top = pd.concat([top, pd.Series({other_label: tail_sum})])
    return top.index.tolist(), top.values.tolist()


def plotly_layout(**kwargs):
    """Base Plotly layout config matching the design system."""
    xaxis_extra = kwargs.pop("xaxis", {})
    yaxis_extra = kwargs.pop("yaxis", {})

    _base_tick = dict(size=10, family="'JetBrains Mono', monospace", color="#78716C")

    # Merge tickfont so callers can override individual keys without a duplicate-key error
    x_tickfont = {**_base_tick, **xaxis_extra.pop("tickfont", {})}
    y_tickfont = {**_base_tick, **yaxis_extra.pop("tickfont", {})}

    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="'Plus Jakarta Sans', ui-sans-serif, sans-serif",
            color="#44403C",
            size=12,
        ),
        margin=dict(t=52, b=44, l=0, r=0),
        bargap=0.38,
        bargroupgap=0.08,
        legend=dict(
            orientation="h",
            y=1.0,
            yanchor="bottom",
            x=0,
            xanchor="left",
            font=dict(size=11, family="'Plus Jakarta Sans', sans-serif"),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        xaxis=dict(
            gridcolor="#EAE8E4",
            gridwidth=0.5,
            linecolor="#EAE8E4",
            showline=False,
            tickfont=x_tickfont,
            title_font=dict(size=11),
            **xaxis_extra,
        ),
        yaxis=dict(
            gridcolor="#EAE8E4",
            gridwidth=0.5,
            linecolor="#EAE8E4",
            showline=False,
            tickfont=y_tickfont,
            title_font=dict(size=11),
            **yaxis_extra,
        ),
    )
    base.update(kwargs)
    return base
