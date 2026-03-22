"""
📈 Trends Analysis
Deep temporal performance analysis with rolling averages, comparisons, and seasonality.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.styles import get_custom_css
from ui.components import render_section_header, render_insight_card, render_filter_chips, render_app_footer, render_kpi_card
from ui.charts import (
    monthly_revenue_line, monthly_revenue_area, cumulative_revenue_chart,
    mom_growth_chart, rolling_average_chart, country_comparison_lines,
    seasonality_heatmap, revenue_distribution_box,
)
from services.data_loader import load_monthly_revenue, load_month_country, load_metadata
from services.metrics import compute_mom_changes, compute_rolling_average, get_trend_insights, format_currency

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Filters ────────────────────────────────────────────────────
sel_ym = st.session_state.get("global_yearmonths", [])
sel_countries = st.session_state.get("global_countries", [])

st.markdown("""
<div class="hero-banner" style="padding: 1.2rem 1.5rem;">
    <h1 style="font-size: 1.6rem;">📈 Trends Analysis</h1>
    <div class="hero-subtitle">Explore temporal patterns, growth rates, rolling averages, and seasonal dynamics.</div>
</div>
""", unsafe_allow_html=True)

render_filter_chips(sel_ym, sel_countries)

# ── Load & filter data ─────────────────────────────────────────
monthly = load_monthly_revenue()
mc = load_month_country()

if sel_ym:
    monthly = monthly[monthly["YearMonth"].isin(sel_ym)]
    mc = mc[mc["YearMonth"].isin(sel_ym)]
if sel_countries:
    mc = mc[mc["Country"].isin(sel_countries)]
    monthly = mc.groupby("YearMonth")["Revenue"].sum().reset_index().sort_values("YearMonth")

if monthly.empty:
    st.warning("No data available for the current filter selection.")
    st.stop()

mom_df = compute_mom_changes(monthly)
insights = get_trend_insights(monthly)

# ── Controls ───────────────────────────────────────────────────
render_section_header("⚙️", "Chart Controls")
ctrl_col1, ctrl_col2 = st.columns(2)
with ctrl_col1:
    chart_type = st.selectbox("Primary Chart Type", ["Line", "Area"], key="trend_chart_type")
with ctrl_col2:
    metadata = load_metadata()
    compare_countries = st.multiselect(
        "Compare Countries",
        options=metadata.get("allowed_countries", []),
        default=sel_countries[:3] if sel_countries else [],
        max_selections=5,
        key="trend_compare",
    )

# ── KPI Row ────────────────────────────────────────────────────
render_section_header("📊", "Trend Summary")
kpi_cols = st.columns(5)
with kpi_cols[0]:
    render_kpi_card("Total Revenue", insights.get("total_revenue", 0), f'{insights.get("total_months", 0)} months', is_currency=True)
with kpi_cols[1]:
    render_kpi_card("Peak Month", insights.get("peak_month", "N/A"), format_currency(insights.get("peak_revenue", 0)))
with kpi_cols[2]:
    render_kpi_card("Weakest Month", insights.get("lowest_month", "N/A"), format_currency(insights.get("lowest_revenue", 0)))
with kpi_cols[3]:
    render_kpi_card("Monthly Average", insights.get("avg_monthly", 0), "Mean revenue", is_currency=True)
with kpi_cols[4]:
    direction = insights.get("trend_direction", "stable")
    icon = "📈" if direction == "upward" else "📉" if direction == "downward" else "➡️"
    render_kpi_card(f"{icon} Trend", direction.title(), f'{insights.get("trend_change_pct", 0):+.1f}%')

# ── Primary Trend Chart ───────────────────────────────────────
render_section_header("📈", "Revenue Over Time")
if chart_type == "Line":
    fig = monthly_revenue_line(monthly, "Monthly Revenue Trend", 420)
else:
    fig = monthly_revenue_area(monthly, "Monthly Revenue Area", 420)
st.plotly_chart(fig, use_container_width=True, key="trends_main")

if insights:
    render_insight_card(
        f"Revenue peaked at <strong>£{insights.get('peak_revenue', 0):,.0f}</strong> in "
        f"<strong>{insights.get('peak_month', 'N/A')}</strong>. "
        f"The overall trend is <strong>{insights.get('trend_direction', 'stable')}</strong> "
        f"with a standard deviation of <strong>£{insights.get('std_monthly', 0):,.0f}</strong> indicating "
        f"{'high' if insights.get('std_monthly', 0) > insights.get('avg_monthly', 1) * 0.3 else 'moderate'} volatility."
    )

# ── Rolling Average & Cumulative ──────────────────────────────
render_section_header("📊", "Advanced Trend Views")
adv_col1, adv_col2 = st.columns(2)
with adv_col1:
    rolling_window = st.slider("Rolling Average Window", 2, 6, 3, key="trend_rolling")
    rolling_df = compute_rolling_average(monthly, rolling_window)
    fig = rolling_average_chart(rolling_df, rolling_window, height=380)
    st.plotly_chart(fig, use_container_width=True, key="trends_rolling")
with adv_col2:
    fig = cumulative_revenue_chart(monthly, "Cumulative Revenue", 380)
    st.plotly_chart(fig, use_container_width=True, key="trends_cumulative")

# ── Growth Rate ────────────────────────────────────────────────
render_section_header("📊", "Growth Analysis")
growth_col1, growth_col2 = st.columns(2)
with growth_col1:
    fig = mom_growth_chart(mom_df, "Month-over-Month Growth Rate (%)", 380)
    st.plotly_chart(fig, use_container_width=True, key="trends_mom")
with growth_col2:
    fig = revenue_distribution_box(monthly, "Revenue Distribution", 380)
    st.plotly_chart(fig, use_container_width=True, key="trends_dist")

# ── Country Comparison ─────────────────────────────────────────
if compare_countries:
    render_section_header("🌍", "Country Trend Comparison")
    fig = country_comparison_lines(mc, compare_countries, height=420)
    st.plotly_chart(fig, use_container_width=True, key="trends_country_compare")

# ── Seasonality ────────────────────────────────────────────────
render_section_header("🗓️", "Seasonality Pattern")
fig = seasonality_heatmap(monthly, "Revenue Seasonality (Year × Month)", 320)
st.plotly_chart(fig, use_container_width=True, key="trends_seasonality")

# ── Monthly KPI Table ──────────────────────────────────────────
render_section_header("📋", "Monthly KPI Table")
display = mom_df.copy()
for col in ["Revenue", "PrevRevenue", "MoM_Change", "Cumulative_Revenue"]:
    if col in display.columns:
        display[col] = display[col].apply(lambda x: f"£{x:,.0f}" if not __import__('math').isnan(x) else "—" if isinstance(x, float) else f"£{x:,.0f}")
if "MoM_Growth_Pct" in display.columns:
    display["MoM_Growth_Pct"] = display["MoM_Growth_Pct"].apply(lambda x: f"{x:+.1f}%" if not __import__('math').isnan(x) else "—" if isinstance(x, float) else f"{x:+.1f}%")

rename_map = {"Revenue": "Revenue (£)", "PrevRevenue": "Prev Month (£)", "MoM_Change": "Change (£)", "MoM_Growth_Pct": "Growth %", "Cumulative_Revenue": "Cumulative (£)"}
display.rename(columns={k: v for k, v in rename_map.items() if k in display.columns}, inplace=True)
cols_show = [c for c in ["YearMonth", "Revenue (£)", "Prev Month (£)", "Change (£)", "Growth %", "Cumulative (£)"] if c in display.columns]
st.dataframe(display[cols_show], use_container_width=True, hide_index=True, height=350)

csv = monthly[["YearMonth", "Revenue"]].to_csv(index=False)
st.download_button("📥 Download Trend Data (CSV)", csv, "monthly_trend.csv", "text/csv", key="trends_download")

render_app_footer()
