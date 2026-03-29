from __future__ import annotations

from datetime import datetime
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.data_access import DashboardRepository


PALETTE = {
    "ink": "#162033",
    "ink_soft": "#5f6b7c",
    "paper": "#f5f7fb",
    "panel": "#ffffff",
    "line": "#e5eaf2",
    "blue": "#2563eb",
    "teal": "#0f766e",
    "amber": "#d97706",
    "coral": "#dc5d47",
    "slate": "#64748b",
    "forest": "#2f6f5e",
}


st.set_page_config(
    page_title="Customer 360 Command Center",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_dashboard_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    repo = DashboardRepository()
    customers = repo.load_customer_view()
    orders = repo.load_order_view()
    support = repo.load_support_view()

    for frame, date_columns in [
        (customers, ["signup_date", "first_order_date", "last_order_date", "signup_cohort_month"]),
        (orders, ["order_date"]),
        (support, ["created_at"]),
    ]:
        for column in date_columns:
            if column in frame.columns:
                frame[column] = pd.to_datetime(frame[column])

    customers["full_name"] = customers["first_name"] + " " + customers["last_name"]
    customers["avg_csat_score"] = customers["avg_csat_score"].fillna(0)
    customers["days_since_last_order"] = customers["days_since_last_order"].fillna(999)
    customers["churn_risk_band"] = customers["churn_risk_band"].fillna("Unknown")
    customers["repeat_purchase_segment"] = customers["repeat_purchase_segment"].fillna("No purchase")

    return customers, orders, support


def apply_styles() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=DM+Sans:wght@400;500;700&display=swap');

            :root {{
                --ink: {PALETTE["ink"]};
                --ink-soft: {PALETTE["ink_soft"]};
                --paper: {PALETTE["paper"]};
                --panel: {PALETTE["panel"]};
                --line: {PALETTE["line"]};
                --blue: {PALETTE["blue"]};
                --teal: {PALETTE["teal"]};
                --amber: {PALETTE["amber"]};
                --coral: {PALETTE["coral"]};
                --slate: {PALETTE["slate"]};
                --forest: {PALETTE["forest"]};
            }}

            .stApp {{
                background: var(--paper);
                color: var(--ink);
                font-family: 'DM Sans', sans-serif;
            }}

            .block-container {{
                max-width: 1320px;
                padding-top: 1.25rem;
                padding-bottom: 2rem;
            }}

            h1, h2, h3, h4 {{
                font-family: 'Space Grotesk', sans-serif !important;
                color: var(--ink);
                letter-spacing: -0.025em;
            }}

            [data-testid="stSidebar"] {{
                background: #ffffff;
                border-right: 1px solid var(--line);
            }}

            [data-testid="stSidebar"] * {{
                color: var(--ink);
                font-family: 'DM Sans', sans-serif;
            }}

            [data-testid="stSidebar"] .stCaption {{
                color: var(--ink-soft);
            }}

            .page-header {{
                padding: 0.25rem 0 0.4rem 0;
                margin-bottom: 0.9rem;
            }}

            .page-kicker {{
                color: var(--blue);
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                font-weight: 700;
            }}

            .page-title {{
                color: var(--ink);
                font-size: 2.4rem;
                line-height: 1.05;
                font-family: 'Space Grotesk', sans-serif;
                font-weight: 700;
                margin: 0.2rem 0 0 0;
            }}

            .page-copy {{
                max-width: 760px;
                color: var(--ink-soft);
                font-size: 0.98rem;
                line-height: 1.65;
                margin-top: 0.75rem;
            }}

            .meta-strip {{
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.75rem;
                margin-top: 1rem;
            }}

            .meta-pill {{
                border: 1px solid var(--line);
                background: var(--panel);
                border-radius: 14px;
                padding: 0.85rem 1rem;
            }}

            .meta-label {{
                color: var(--ink-soft);
                font-size: 0.74rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}

            .meta-value {{
                color: var(--ink);
                font-size: 1rem;
                font-weight: 600;
                margin-top: 0.2rem;
            }}

            .kpi-card {{
                min-height: 132px;
                padding: 1rem;
                border-radius: 16px;
                border: 1px solid var(--line);
                background: var(--panel);
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
            }}

            .kpi-label {{
                color: var(--ink-soft);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-size: 0.72rem;
                font-weight: 700;
            }}

            .kpi-value {{
                color: var(--ink);
                font-family: 'Space Grotesk', sans-serif;
                font-size: 2rem;
                font-weight: 700;
                margin-top: 0.35rem;
            }}

            .kpi-delta {{
                margin-top: 0.45rem;
                color: var(--ink-soft);
                font-size: 0.88rem;
            }}

            .section-label {{
                color: var(--ink-soft);
                text-transform: uppercase;
                letter-spacing: 0.12em;
                font-size: 0.72rem;
                font-weight: 700;
            }}

            [data-testid="stTabs"] button {{
                font-family: 'Space Grotesk', sans-serif;
                color: var(--ink-soft);
            }}

            [data-testid="stTabs"] button[aria-selected="true"] {{
                color: var(--ink);
            }}

            [data-testid="stPlotlyChart"], .stDataFrame {{
                background: var(--panel);
                border: 1px solid var(--line);
                border-radius: 16px;
                padding: 0.2rem;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
            }}

            .insight-card {{
                height: 100%;
                padding: 1rem;
                border-radius: 16px;
                border: 1px solid var(--line);
                background: var(--panel);
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def money(value: float) -> str:
    return f"${value:,.0f}"


def compact_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def build_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="DM Sans", color=PALETTE["ink"]),
        margin=dict(l=16, r=16, t=56, b=16),
        title_font=dict(family="Space Grotesk", size=18, color=PALETTE["ink"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(showgrid=False, zeroline=False, linecolor=PALETTE["line"]),
        yaxis=dict(gridcolor="rgba(22,32,51,0.08)", zeroline=False),
    )
    return fig


def filter_frames(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    support: pd.DataFrame,
    channels: list[str],
    churn_bands: list[str],
    cities: list[str],
    repeat_segments: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    filtered_customers = customers.copy()
    if channels:
        filtered_customers = filtered_customers[filtered_customers["acquisition_channel"].isin(channels)]
    if churn_bands:
        filtered_customers = filtered_customers[filtered_customers["churn_risk_band"].isin(churn_bands)]
    if cities:
        filtered_customers = filtered_customers[filtered_customers["city"].isin(cities)]
    if repeat_segments:
        filtered_customers = filtered_customers[filtered_customers["repeat_purchase_segment"].isin(repeat_segments)]

    customer_ids = filtered_customers["customer_id"].unique().tolist()
    filtered_orders = orders[orders["customer_id"].isin(customer_ids)].copy()
    filtered_support = support[support["customer_id"].isin(customer_ids)].copy()
    return filtered_customers, filtered_orders, filtered_support


def render_hero(filtered_customers: pd.DataFrame, filtered_orders: pd.DataFrame) -> None:
    total_revenue = filtered_customers["lifetime_revenue"].sum()
    total_customers = len(filtered_customers)
    high_risk = int((filtered_customers["churn_risk_band"] == "High").sum())
    repeat_rate = 100 * filtered_customers["is_repeat_customer"].mean() if total_customers else 0
    last_refresh = datetime.now().strftime("%d %b %Y, %I:%M %p")

    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-kicker">Customer 360 Analytics Warehouse</div>
            <h1 class="page-title">Customer command center for value, loyalty, and churn.</h1>
            <div class="page-copy">
                Explore lifecycle health across acquisition, revenue, support, and repeat behavior using marts built from the Customer 360 warehouse.
                The dashboard reads directly from DuckDB and reflects the same ETL and modeling pipeline used in the project.
            </div>
            <div class="meta-strip">
                <div class="meta-pill">
                    <div class="meta-label">Revenue in scope</div>
                    <div class="meta-value">{money(total_revenue)}</div>
                </div>
                <div class="meta-pill">
                    <div class="meta-label">Customers in focus</div>
                    <div class="meta-value">{compact_number(total_customers)}</div>
                </div>
                <div class="meta-pill">
                    <div class="meta-label">Last dashboard refresh</div>
                    <div class="meta-value">{last_refresh}</div>
                </div>
            </div>
            <div class="page-copy" style="margin-top:0.75rem;">
                Repeat rate is <strong>{repeat_rate:.1f}%</strong> and <strong>{high_risk}</strong> customers currently sit in the high-risk churn band across the selected population.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, delta: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_overview_charts(filtered_customers: pd.DataFrame, filtered_orders: pd.DataFrame) -> tuple[go.Figure, go.Figure, go.Figure]:
    revenue_trend = (
        filtered_orders.assign(order_month=filtered_orders["order_date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["order_month", "acquisition_channel"], as_index=False)["recognized_revenue"]
        .sum()
    )
    fig_revenue = px.area(
        revenue_trend,
        x="order_month",
        y="recognized_revenue",
        color="acquisition_channel",
        color_discrete_sequence=[PALETTE["blue"], PALETTE["teal"], PALETTE["amber"], PALETTE["coral"], PALETTE["slate"], PALETTE["forest"]],
        title="Revenue Momentum by Channel",
    )
    fig_revenue.update_traces(mode="lines", line=dict(width=2), stackgroup="one")

    channel_view = (
        filtered_customers.groupby("acquisition_channel", as_index=False)
        .agg(customers=("customer_id", "count"), revenue=("lifetime_revenue", "sum"), repeat_rate=("is_repeat_customer", "mean"))
        .sort_values("revenue", ascending=False)
    )
    fig_channel = px.bar(
        channel_view,
        x="acquisition_channel",
        y="revenue",
        color="repeat_rate",
        color_continuous_scale=[PALETTE["coral"], PALETTE["amber"], PALETTE["teal"]],
        text_auto=".2s",
        title="Channel Contribution vs Repeat Strength",
    )
    fig_channel.update_coloraxes(colorbar_title="Repeat rate")

    risk_mix = (
        filtered_customers.groupby(["churn_risk_band", "repeat_purchase_segment"], as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "customers"})
    )
    segment_order = ["No purchase", "One-time", "Second-time", "Repeat", "Habit"]
    fig_risk = px.bar(
        risk_mix,
        x="churn_risk_band",
        y="customers",
        color="repeat_purchase_segment",
        category_orders={"repeat_purchase_segment": segment_order, "churn_risk_band": ["Low", "Medium", "High", "Unknown"]},
        color_discrete_sequence=[PALETTE["slate"], PALETTE["amber"], PALETTE["coral"], PALETTE["teal"], PALETTE["ink"]],
        title="Risk Composition Across Purchase Segments",
    )

    return build_theme(fig_revenue), build_theme(fig_channel), build_theme(fig_risk)


def make_value_charts(filtered_customers: pd.DataFrame) -> tuple[go.Figure, go.Figure]:
    scatter = px.scatter(
        filtered_customers,
        x="churn_risk_score",
        y="blended_clv",
        size="completed_orders",
        color="acquisition_channel",
        hover_name="full_name",
        hover_data={"customer_id": True, "city": True, "completed_orders": True, "churn_risk_score": True, "blended_clv": ":.2f"},
        color_discrete_sequence=[PALETTE["blue"], PALETTE["teal"], PALETTE["amber"], PALETTE["coral"], PALETTE["slate"], PALETTE["forest"]],
        title="High-Value vs High-Risk Customer Map",
    )
    scatter.update_traces(marker=dict(opacity=0.82, line=dict(width=0.8, color="rgba(255,255,255,0.7)")))

    top_value = (
        filtered_customers.nlargest(12, "blended_clv")[["full_name", "blended_clv", "recommended_action"]]
        .sort_values("blended_clv")
    )
    fig_top = px.bar(
        top_value,
        x="blended_clv",
        y="full_name",
        orientation="h",
        color="blended_clv",
        color_continuous_scale=[PALETTE["blue"], PALETTE["teal"], PALETTE["ink"]],
        title="Top 12 Customers by Blended CLV",
        hover_data={"recommended_action": True},
    )

    return build_theme(scatter), build_theme(fig_top)


def make_retention_charts(filtered_customers: pd.DataFrame) -> tuple[go.Figure, go.Figure]:
    cohort = (
        filtered_customers.groupby(["signup_cohort_month", "acquisition_channel"], as_index=False)
        .agg(cohort_repeat_rate_pct=("cohort_repeat_rate_pct", "mean"), customers=("customer_id", "count"))
        .sort_values("signup_cohort_month")
    )
    fig_cohort = px.line(
        cohort,
        x="signup_cohort_month",
        y="cohort_repeat_rate_pct",
        color="acquisition_channel",
        markers=True,
        color_discrete_sequence=[PALETTE["blue"], PALETTE["teal"], PALETTE["amber"], PALETTE["coral"], PALETTE["slate"], PALETTE["forest"]],
        title="Cohort Repeat Rate by Acquisition Channel",
    )

    purchase_gap = px.box(
        filtered_customers[filtered_customers["avg_days_between_orders"].notna()],
        x="repeat_purchase_segment",
        y="avg_days_between_orders",
        color="repeat_purchase_segment",
        category_orders={"repeat_purchase_segment": ["One-time", "Second-time", "Repeat", "Habit"]},
        color_discrete_sequence=[PALETTE["amber"], PALETTE["coral"], PALETTE["teal"], PALETTE["ink"]],
        title="Order Cadence Distribution by Repeat Segment",
    )

    return build_theme(fig_cohort), build_theme(purchase_gap)


def make_support_charts(filtered_support: pd.DataFrame, filtered_customers: pd.DataFrame) -> tuple[go.Figure, go.Figure]:
    issue_mix = (
        filtered_support.groupby(["issue_type", "priority"], as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "tickets"})
    )
    fig_issue = px.bar(
        issue_mix,
        x="issue_type",
        y="tickets",
        color="priority",
        barmode="group",
        color_discrete_map={"Low": PALETTE["teal"], "Medium": PALETTE["amber"], "High": PALETTE["coral"]},
        title="Support Load by Issue Type and Priority",
    )

    csat_band = (
        filtered_customers.assign(csat_band=pd.cut(filtered_customers["avg_csat_score"], bins=[-0.1, 0.1, 2.5, 3.5, 5.0], labels=["No data", "At risk", "Needs work", "Healthy"]))
        .groupby(["csat_band", "churn_risk_band"], as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "customers"})
    )
    fig_csat = px.bar(
        csat_band,
        x="csat_band",
        y="customers",
        color="churn_risk_band",
        category_orders={"csat_band": ["No data", "At risk", "Needs work", "Healthy"], "churn_risk_band": ["Low", "Medium", "High", "Unknown"]},
        color_discrete_map={"Low": PALETTE["teal"], "Medium": PALETTE["amber"], "High": PALETTE["coral"], "Unknown": PALETTE["slate"]},
        title="CSAT Health vs Churn Risk",
    )

    return build_theme(fig_issue), build_theme(fig_csat)


def render_insight(label: str, headline: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="section-label">{label}</div>
            <h3 style="margin:0.35rem 0 0.5rem 0;">{headline}</h3>
            <div style="color:{PALETTE["ink_soft"]}; line-height:1.65;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    apply_styles()
    customers, orders, support = load_dashboard_frames()

    with st.sidebar:
        st.markdown("## Customer 360")
        st.caption("Warehouse-backed dashboard")
        channel_options = sorted(customers["acquisition_channel"].dropna().unique().tolist())
        churn_options = ["High", "Medium", "Low", "Unknown"]
        city_options = sorted(customers["city"].dropna().unique().tolist())
        repeat_options = ["Habit", "Repeat", "Second-time", "One-time", "No purchase"]

        selected_channels = st.multiselect("Acquisition channels", channel_options, default=channel_options)
        selected_churn = st.multiselect("Churn bands", churn_options, default=churn_options)
        selected_cities = st.multiselect("Cities", city_options, default=city_options)
        selected_repeat = st.multiselect("Repeat segments", repeat_options, default=repeat_options)
        st.caption("Tip: use broad filters first, then zoom in on one channel or churn band.")

    filtered_customers, filtered_orders, filtered_support = filter_frames(
        customers,
        orders,
        support,
        selected_channels,
        selected_churn,
        selected_cities,
        selected_repeat,
    )

    if filtered_customers.empty:
        st.warning("No customers match the current filters. Broaden the sidebar selections to bring the dashboard back into scope.")
        st.stop()

    render_hero(filtered_customers, filtered_orders)
    st.write("")

    total_customers = len(filtered_customers)
    repeat_rate = 100 * filtered_customers["is_repeat_customer"].mean() if total_customers else 0
    avg_clv = filtered_customers["blended_clv"].mean() if total_customers else 0
    avg_csat = filtered_customers["avg_csat_score"].replace(0, pd.NA).dropna().mean() if total_customers else 0
    high_risk_share = 100 * (filtered_customers["churn_risk_band"] == "High").mean() if total_customers else 0

    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        render_kpi_card("Customers in scope", compact_number(total_customers), f"{compact_number(filtered_customers['completed_orders'].sum())} completed orders")
    with kpi_cols[1]:
        render_kpi_card("Average blended CLV", money(avg_clv), f"{high_risk_share:.1f}% high-risk share")
    with kpi_cols[2]:
        render_kpi_card("Repeat customer rate", f"{repeat_rate:.1f}%", f"{money(filtered_customers['lifetime_revenue'].sum())} lifetime revenue")
    with kpi_cols[3]:
        render_kpi_card("Average CSAT", f"{avg_csat:.2f}" if pd.notna(avg_csat) else "N/A", f"{filtered_support.shape[0]} support tickets in view")

    overview_tab, value_tab, retention_tab, operations_tab = st.tabs(
        ["Overview", "Value Signals", "Retention", "Support Ops"]
    )

    with overview_tab:
        overview_a, overview_b = st.columns([1.65, 1])
        fig_revenue, fig_channel, fig_risk = make_overview_charts(filtered_customers, filtered_orders)
        overview_a.plotly_chart(fig_revenue, use_container_width=True)
        overview_b.plotly_chart(fig_channel, use_container_width=True)
        st.plotly_chart(fig_risk, use_container_width=True)

        insight_left, insight_right = st.columns(2)
        top_channel = (
            filtered_customers.groupby("acquisition_channel")["lifetime_revenue"].sum().sort_values(ascending=False).index[0]
            if total_customers
            else "N/A"
        )
        repeat_segment = (
            filtered_customers["repeat_purchase_segment"].value_counts().index[0]
            if total_customers
            else "N/A"
        )
        with insight_left:
            render_insight(
                "Commercial lens",
                f"{top_channel} is leading the current revenue mix.",
                "Use this view to compare whether revenue-leading channels also sustain stronger repeat behavior, not just acquisition volume.",
            )
        with insight_right:
            render_insight(
                "Lifecycle lens",
                f"The dominant purchase state is {repeat_segment}.",
                "This tells you whether the portfolio leans toward first-time conversion, early repeat development, or habit-forming retention.",
            )

    with value_tab:
        value_a, value_b = st.columns([1.35, 1])
        fig_scatter, fig_top = make_value_charts(filtered_customers)
        value_a.plotly_chart(fig_scatter, use_container_width=True)
        value_b.plotly_chart(fig_top, use_container_width=True)

        focus_table = (
            filtered_customers.sort_values(["churn_risk_score", "blended_clv"], ascending=[False, False])[
                ["full_name", "acquisition_channel", "city", "blended_clv", "churn_risk_band", "recommended_action"]
            ]
            .head(12)
            .rename(columns={"full_name": "Customer", "acquisition_channel": "Channel", "city": "City", "blended_clv": "Blended CLV", "churn_risk_band": "Risk", "recommended_action": "Action"})
        )
        st.dataframe(focus_table, use_container_width=True, hide_index=True)

    with retention_tab:
        retention_a, retention_b = st.columns([1.25, 1])
        fig_cohort, fig_gap = make_retention_charts(filtered_customers)
        retention_a.plotly_chart(fig_cohort, use_container_width=True)
        retention_b.plotly_chart(fig_gap, use_container_width=True)

        cohort_snapshot = (
            filtered_customers.groupby("repeat_purchase_segment", as_index=False)
            .agg(customers=("customer_id", "count"), avg_gap=("avg_days_between_orders", "mean"))
            .sort_values("customers", ascending=False)
        )
        st.dataframe(cohort_snapshot, use_container_width=True, hide_index=True)

    with operations_tab:
        ops_a, ops_b = st.columns([1.2, 1])
        fig_issue, fig_csat = make_support_charts(filtered_support, filtered_customers)
        ops_a.plotly_chart(fig_issue, use_container_width=True)
        ops_b.plotly_chart(fig_csat, use_container_width=True)

        support_table = (
            filtered_customers.sort_values(["total_tickets", "avg_resolution_hours"], ascending=[False, False])[
                ["full_name", "total_tickets", "high_priority_tickets", "avg_resolution_hours", "avg_csat_score", "churn_risk_band"]
            ]
            .head(12)
            .rename(columns={"full_name": "Customer", "total_tickets": "Tickets", "high_priority_tickets": "High priority", "avg_resolution_hours": "Avg resolution hours", "avg_csat_score": "Avg CSAT", "churn_risk_band": "Risk"})
        )
        st.dataframe(support_table, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
