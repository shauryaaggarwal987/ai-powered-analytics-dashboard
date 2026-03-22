"""
📊 Overview / Executive Dashboard
Premium landing page with KPI cards and interactive analytics charts.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.styles import get_custom_css
from ui.components import render_hero_banner, render_kpi_card, render_section_header, render_insight_card, render_filter_chips, render_app_footer
from ui.charts import (
    monthly_revenue_line, top_countries_bar, top_products_bar,
    country_donut, revenue_share_stacked, revenue_distribution_box,
)
from services.data_loader import (
    load_monthly_revenue, load_country_revenue, load_top_products,
    load_month_country, load_month_product, load_metadata,
)
from services.metrics import get_overview_kpis, format_currency, get_trend_insights, get_country_insights

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Filters ────────────────────────────────────────────────────
sel_ym = st.session_state.get("global_yearmonths", [])
sel_countries = st.session_state.get("global_countries", [])
top_n = st.session_state.get("global_top_n", 10)

# ── Hero ───────────────────────────────────────────────────────
render_hero_banner(
    "AI-Powered Analytics Dashboard",
    "Natural language → Grounded analytics → Deterministic Power BI generation",
    "Explore retail performance, discover trends, and generate tailored Power BI dashboards using AI-driven, metadata-grounded intelligence."
)

render_filter_chips(sel_ym, sel_countries)

# ── KPI Cards ──────────────────────────────────────────────────
render_section_header("📊", "Key Performance Indicators")
kpis = get_overview_kpis()

row1 = st.columns(5)
with row1[0]:
    render_kpi_card("Total Revenue", kpis.get("total_revenue", 0), "All-time processed", is_currency=True)
with row1[1]:
    render_kpi_card("Total Orders", kpis.get("num_orders", 0), "Unique invoices")
with row1[2]:
    render_kpi_card("Unique Customers", kpis.get("unique_customers", 0), "Distinct IDs")
with row1[3]:
    render_kpi_card("Avg Order Value", kpis.get("avg_order_value", 0), "Per invoice", is_currency=True)
with row1[4]:
    render_kpi_card("Time Span", kpis.get("date_range", "N/A"), f'{kpis.get("num_months", 0)} months')

row2 = st.columns(5)
with row2[0]:
    render_kpi_card("Countries", kpis.get("num_countries", 0), "Markets covered")
with row2[1]:
    render_kpi_card("Products", kpis.get("num_products", 0), "Unique items")
with row2[2]:
    render_kpi_card("Best Month", kpis.get("best_month", "N/A"), format_currency(kpis.get("best_month_revenue", 0)))
with row2[3]:
    render_kpi_card("Top Country", kpis.get("best_country", "N/A"), format_currency(kpis.get("best_country_revenue", 0)))
with row2[4]:
    bprod = kpis.get("best_product", "N/A")
    bprod_display = bprod[:22] + "…" if len(str(bprod)) > 22 else bprod
    render_kpi_card("Top Product", bprod_display, format_currency(kpis.get("best_product_revenue", 0)))

# ── Load Data ──────────────────────────────────────────────────
monthly = load_monthly_revenue()
country = load_country_revenue()
products = load_top_products()
mc = load_month_country()
mp = load_month_product()

# Apply filters
if sel_ym:
    monthly = monthly[monthly["YearMonth"].isin(sel_ym)]
    mc = mc[mc["YearMonth"].isin(sel_ym)]
    mp = mp[mp["YearMonth"].isin(sel_ym)]
if sel_countries:
    mc = mc[mc["Country"].isin(sel_countries)]
    country_filtered = mc.groupby("Country")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
else:
    country_filtered = country.copy()

if sel_ym and not sel_countries:
    country_filtered = mc.groupby("Country")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)

# Filter products from month_product if yearmonth selected
if sel_ym:
    products_filtered = mp.groupby("Description")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
else:
    products_filtered = products.copy()

# ── Primary Analytics Row ──────────────────────────────────────
render_section_header("📈", "Revenue Trends & Country Performance")

col_trend, col_country = st.columns([3, 2])
with col_trend:
    fig = monthly_revenue_line(monthly, "Monthly Revenue Trend")
    st.plotly_chart(fig, use_container_width=True, key="overview_trend")
with col_country:
    fig = country_donut(country_filtered, top_n, "Revenue Share by Country")
    st.plotly_chart(fig, use_container_width=True, key="overview_donut")

# Trend insights
if not monthly.empty:
    insights = get_trend_insights(monthly)
    if insights:
        render_insight_card(
            f"Revenue peaked in <strong>{insights.get('peak_month', 'N/A')}</strong> "
            f"(£{insights.get('peak_revenue', 0):,.0f}). "
            f"Weakest month: <strong>{insights.get('lowest_month', 'N/A')}</strong> "
            f"(£{insights.get('lowest_revenue', 0):,.0f}). "
            f"Overall trend is <strong>{insights.get('trend_direction', 'stable')}</strong> "
            f"({insights.get('trend_change_pct', 0):+.1f}% half-over-half)."
        )

# ── Secondary Analytics Row ────────────────────────────────────
render_section_header("🏆", "Top Performers")

col_bars1, col_bars2 = st.columns(2)
with col_bars1:
    fig = top_countries_bar(country_filtered, top_n, f"Top {top_n} Countries")
    st.plotly_chart(fig, use_container_width=True, key="overview_countries_bar")
with col_bars2:
    fig = top_products_bar(products_filtered, top_n, f"Top {top_n} Products")
    st.plotly_chart(fig, use_container_width=True, key="overview_products_bar")

# Country insights
if not country_filtered.empty:
    c_insights = get_country_insights(country_filtered, top_n)
    if c_insights:
        render_insight_card(
            f"<strong>{c_insights.get('top_country', 'N/A')}</strong> leads with "
            f"{c_insights.get('top_country_share', 0):.1f}% of filtered revenue. "
            f"Top {top_n} countries account for <strong>{c_insights.get('top_n_share', 0):.1f}%</strong> "
            f"across {c_insights.get('num_countries', 0)} markets."
        )


# ── Composition Row ────────────────────────────────────────────
render_section_header("📊", "Revenue Composition & Distribution")

col_comp, col_dist = st.columns([3, 2])
with col_comp:
    fig = revenue_share_stacked(mc, min(top_n, 8), "Revenue Composition by Country")
    st.plotly_chart(fig, use_container_width=True, key="overview_stacked")
with col_dist:
    fig = revenue_distribution_box(monthly, "Monthly Revenue Distribution")
    st.plotly_chart(fig, use_container_width=True, key="overview_box")

# ── Summary Table ──────────────────────────────────────────────
render_section_header("📋", "Monthly Summary Table")
if not monthly.empty:
    display_monthly = monthly.copy()
    display_monthly["Revenue (£)"] = display_monthly["Revenue"].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(
        display_monthly[["YearMonth", "Revenue (£)"]],
        use_container_width=True,
        hide_index=True,
        height=300,
    )
else:
    st.info("No monthly data available for the current filter selection.")

render_app_footer()
