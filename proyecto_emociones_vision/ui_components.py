import time
import pandas as pd
import plotly.express as px
import streamlit as st

import config


def render_chart(counts: dict[str, int], chart_placeholder) -> None:

    df = pd.DataFrame([
        {"Emoción": emocion, "Cantidad": cantidad}
        for emocion, cantidad in counts.items()
    ])

    fig = px.bar(
        df,
        y="Emoción",
        x="Cantidad",
        color="Emoción",
        orientation="h",
        color_discrete_map=config.COLORS_HEX,
        text="Cantidad",
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=10, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor="#334155",
            title="Número de Personas",
        ),
        yaxis=dict(
            title="",
            categoryorder="array",
            categoryarray=config.CHART_CATEGORY_ORDER,
        ),
        showlegend=False,
        height=350,
        font=dict(family="Inter, sans-serif", size=13),
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker=dict(line=dict(width=1.5, color="#ffffff")),
    )

    chart_placeholder.plotly_chart(
        fig,
        use_container_width=True,
        key=f"chart_{time.time()}",
    )


def render_metric_card(counts: dict[str, int], metric_placeholder) -> None:

    total = sum(counts.values())
    metric_placeholder.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{total}</div>
            <div class="metric-label">Personas Registradas en Total</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_event_log(event_log: list[str], log_placeholder) -> None:

    recent = event_log[-5:]

    if not recent:
        log_placeholder.markdown(
            "<p style='color:#64748b;'>No hay eventos registrados aún.</p>",
            unsafe_allow_html=True,
        )
        return

    html_content = "".join(
        f'<div class="event-log">{evento}</div>'
        for evento in reversed(recent)
    )
    log_placeholder.markdown(html_content, unsafe_allow_html=True)
