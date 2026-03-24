"""
🌍 Geography / Country Analysis
Country-level insights with rankings, contributions, heatmaps, and drill-down.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.styles import get_custom_css
from ui.components import render_section_header, render_insight_card, render_kpi_card, render_filter_chips, render_app_footer, render_empty_state
from ui.charts import top_countries_bar, country_donut, country_treemap, country_comparison_lines
from services.data_loader import load_country_revenue, load_month_country, load_metadata
from services.metrics import compute_country_shares, get_country_insights, format_currency

st.markdown(get_custom_css(), unsafe_allow_html=True)

sel_ym = st.session_state.get("global_yearmonths", [])
sel_countries = st.session_state.get("global_countries", [])
top_n = st.session_state.get("global_top_n", 10)

st.markdown("""
<div class="hero-banner" style="padding: 1.2rem 1.5rem;">
    <h1 style="font-size: 1.6rem;">🌍 Geography & Country Analysis</h1>
    <div class="hero-subtitle">Explore market distribution, country rankings, and regional performance patterns.</div>
</div>
""", unsafe_allow_html=True)

render_filter_chips(sel_ym, sel_countries)

# ── Load data ──────────────────────────────────────────────────
country_all = load_country_revenue()
mc = load_month_country()

if sel_ym:
    mc = mc[mc["YearMonth"].isin(sel_ym)]
    country_df = mc.groupby("Country")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
else:
    country_df = country_all.copy()

if sel_countries:
    mc = mc[mc["Country"].isin(sel_countries)]
    country_df = country_df[country_df["Country"].isin(sel_countries)]

if country_df.empty:
    render_empty_state("🌍", "No country data", "No data found for the current filter selection. Try adjusting your filters.")
    st.stop()

country_shares = compute_country_shares(country_df)
c_insights = get_country_insights(country_df, top_n)

# ── Controls ───────────────────────────────────────────────────
render_section_header("⚙️", "Controls")
ctrl1, ctrl2, ctrl3 = st.columns(3)
with ctrl1:
    display_top_n = st.slider("Top N Countries", 5, min(30, len(country_df)), min(top_n, len(country_df)), key="geo_top_n")
with ctrl2:
    chart_mode = st.selectbox("Chart View", ["Bar + Donut", "Treemap", "Both"], key="geo_chart_mode")
with ctrl3:
    country_search = st.text_input("🔍 Search Country", key="geo_search")

if country_search:
    country_df = country_df[country_df["Country"].str.contains(country_search, case=False, na=False)]
    country_shares = compute_country_shares(country_df)

# ── KPI Row ────────────────────────────────────────────────────
render_section_header("📊", "Country Performance Summary")
k_cols = st.columns(4)
with k_cols[0]:
    render_kpi_card("Total Markets", len(country_df), "Active countries")
with k_cols[1]:
    render_kpi_card("Top Country", c_insights.get("top_country", "N/A"), f'{c_insights.get("top_country_share", 0):.1f}% share')
with k_cols[2]:
    render_kpi_card(f"Top {display_top_n} Share", f'{country_shares.head(display_top_n)["Share_Pct"].sum():.1f}%', "Revenue concentration")
with k_cols[3]:
    render_kpi_card("Total Revenue", c_insights.get("total_revenue", 0), "Filtered total", is_currency=True)

# ── Main Charts ────────────────────────────────────────────────
render_section_header("📊", "Country Revenue Distribution")

if chart_mode in ["Bar + Donut", "Both"]:
    c1, c2 = st.columns([3, 2])
    with c1:
        fig = top_countries_bar(country_df, display_top_n, f"Top {display_top_n} Countries by Revenue")
        st.plotly_chart(fig, use_container_width=True, key="geo_bar")
    with c2:
        fig = country_donut(country_df, display_top_n, "Revenue Share")
        st.plotly_chart(fig, use_container_width=True, key="geo_donut")

if chart_mode in ["Treemap", "Both"]:
    fig = country_treemap(country_df, display_top_n, "Revenue Treemap by Country")
    st.plotly_chart(fig, use_container_width=True, key="geo_treemap")

render_insight_card(
    f"<strong>{c_insights.get('top_country', 'N/A')}</strong> contributes "
    f"<strong>{c_insights.get('top_country_share', 0):.1f}%</strong> of filtered revenue. "
    f"The top {display_top_n} countries account for "
    f"<strong>{country_shares.head(display_top_n)['Share_Pct'].sum():.1f}%</strong> "
    f"of total revenue across {len(country_df)} markets."
)


# ── Country Comparison ─────────────────────────────────────────
render_section_header("📈", "Country Trend Comparison")
metadata = load_metadata()
compare_countries = st.multiselect(
    "Select countries to compare",
    options=metadata.get("allowed_countries", []),
    default=country_df.head(3)["Country"].tolist(),
    max_selections=6,
    key="geo_compare",
)
if compare_countries:
    mc_full = load_month_country()
    if sel_ym:
        mc_full = mc_full[mc_full["YearMonth"].isin(sel_ym)]
    fig = country_comparison_lines(mc_full, compare_countries, height=420)
    st.plotly_chart(fig, use_container_width=True, key="geo_compare_chart")

# ── Country Detail Drill-Down ──────────────────────────────────
render_section_header("🔍", "Country Deep Dive")
selected_country = st.selectbox("Select a country", country_df["Country"].tolist(), key="geo_drilldown")

if selected_country:
    mc_country = mc[mc["Country"] == selected_country]
    country_total = float(country_df[country_df["Country"] == selected_country]["Revenue"].sum())
    global_total = float(country_df["Revenue"].sum())
    share = (country_total / global_total * 100) if global_total > 0 else 0

    d_cols = st.columns(4)
    with d_cols[0]:
        render_kpi_card("Total Revenue", country_total, selected_country, is_currency=True)
    with d_cols[1]:
        render_kpi_card("Global Share", f"{share:.1f}%", "Of filtered revenue")
    with d_cols[2]:
        best_month = mc_country.loc[mc_country["Revenue"].idxmax(), "YearMonth"] if not mc_country.empty else "N/A"
        render_kpi_card("Best Month", best_month, "Highest revenue period")
    with d_cols[3]:
        rank = list(country_df["Country"]).index(selected_country) + 1 if selected_country in country_df["Country"].values else "N/A"
        render_kpi_card("Rank", f"#{rank}", f"Out of {len(country_df)}")

    if not mc_country.empty:
        fig = country_comparison_lines(mc, [selected_country], f"{selected_country} — Monthly Trend", 350)
        st.plotly_chart(fig, use_container_width=True, key="geo_drilldown_chart")

# ── Ranking Table ──────────────────────────────────────────────
render_section_header("📋", "Country Ranking Table")
display = country_shares.copy()
display["Revenue (£)"] = display["Revenue"].apply(lambda x: f"£{x:,.2f}")
display["Share"] = display["Share_Pct"].apply(lambda x: f"{x:.2f}%")
display["Cumulative"] = display["Cumulative_Share"].apply(lambda x: f"{x:.1f}%")
display.insert(0, "Rank", range(1, len(display) + 1))
st.dataframe(display[["Rank", "Country", "Revenue (£)", "Share", "Cumulative"]], use_container_width=True, hide_index=True, height=400)

csv = country_shares[["Country", "Revenue", "Share_Pct"]].to_csv(index=False)
st.download_button("📥 Download Country Data (CSV)", csv, "country_analysis.csv", "text/csv", key="geo_download")

render_app_footer()
