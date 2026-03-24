"""
📦 Product Insights
Product-level analysis with rankings, trends, heatmaps, and drill-down.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.styles import get_custom_css
from ui.components import render_section_header, render_insight_card, render_kpi_card, render_filter_chips, render_app_footer, render_empty_state
from ui.charts import top_products_bar, product_treemap, pareto_chart, product_comparison_lines, country_donut
from services.data_loader import load_top_products, load_month_product, load_month_country
from services.metrics import compute_product_shares, format_currency

st.markdown(get_custom_css(), unsafe_allow_html=True)

sel_ym = st.session_state.get("global_yearmonths", [])
sel_countries = st.session_state.get("global_countries", [])
top_n = st.session_state.get("global_top_n", 10)

st.markdown("""
<div class="hero-banner" style="padding: 1.2rem 1.5rem;">
    <h1 style="font-size: 1.6rem;">📦 Product Insights</h1>
    <div class="hero-subtitle">Discover top-performing products, revenue concentration, and product trends over time.</div>
</div>
""", unsafe_allow_html=True)

render_filter_chips(sel_ym, sel_countries)

# ── Load data ──────────────────────────────────────────────────
products_all = load_top_products()
mp = load_month_product()

if sel_ym:
    mp = mp[mp["YearMonth"].isin(sel_ym)]
    products_df = mp.groupby("Description")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
else:
    products_df = products_all.copy()

if products_df.empty:
    render_empty_state("📦", "No product data", "No data found for the current filter selection.")
    st.stop()

# ── Controls ───────────────────────────────────────────────────
render_section_header("⚙️", "Controls")
ctrl1, ctrl2 = st.columns(2)
with ctrl1:
    display_top_n = st.slider("Top N Products", 5, min(30, len(products_df)), min(top_n, len(products_df)), key="prod_top_n")
with ctrl2:
    product_search = st.text_input("🔍 Search Product", key="prod_search")

if product_search:
    products_df = products_df[products_df["Description"].str.contains(product_search, case=False, na=False)]

if products_df.empty:
    render_empty_state("🔍", "No products match", f'No products found matching "{product_search}".')
    st.stop()

product_shares = compute_product_shares(products_df.head(display_top_n))

# ── KPI Row ────────────────────────────────────────────────────
render_section_header("📊", "Product Performance Summary")
total_products = len(products_df)
top_product = products_df.iloc[0]["Description"] if not products_df.empty else "N/A"
top_product_rev = float(products_df.iloc[0]["Revenue"]) if not products_df.empty else 0
total_rev = float(products_df["Revenue"].sum())
top_n_rev = float(products_df.head(display_top_n)["Revenue"].sum())
top_n_share = (top_n_rev / total_rev * 100) if total_rev > 0 else 0

k_cols = st.columns(4)
with k_cols[0]:
    render_kpi_card("Total Products", total_products, "In filtered view")
with k_cols[1]:
    label = top_product[:20] + "…" if len(top_product) > 20 else top_product
    render_kpi_card("#1 Product", label, format_currency(top_product_rev))
with k_cols[2]:
    render_kpi_card(f"Top {display_top_n} Share", f"{top_n_share:.1f}%", "Revenue concentration")
with k_cols[3]:
    render_kpi_card("Total Revenue", total_rev, "All products", is_currency=True)

# ── Main Charts ────────────────────────────────────────────────
render_section_header("📊", "Product Revenue Analysis")
c1, c2 = st.columns([3, 2])
with c1:
    fig = top_products_bar(products_df, display_top_n, f"Top {display_top_n} Products by Revenue")
    st.plotly_chart(fig, use_container_width=True, key="prod_bar")
with c2:
    fig = product_treemap(products_df, display_top_n, "Product Revenue Treemap")
    st.plotly_chart(fig, use_container_width=True, key="prod_treemap")

render_insight_card(
    f"The top product, <strong>{top_product[:35]}</strong>, "
    f"generated <strong>{format_currency(top_product_rev)}</strong>. "
    f"The top {display_top_n} products account for <strong>{top_n_share:.1f}%</strong> "
    f"of total product revenue, indicating {'high' if top_n_share > 60 else 'moderate'} concentration."
)

# ── Pareto Analysis ────────────────────────────────────────────
render_section_header("📊", "Pareto Analysis (80/20 Rule)")
fig = pareto_chart(products_df, "Revenue", "Description", display_top_n, "Product Revenue Pareto", 420)
st.plotly_chart(fig, use_container_width=True, key="prod_pareto")


# ── Product Trend Comparison ───────────────────────────────────
render_section_header("📈", "Product Trend Comparison")
avail_products = products_df.head(20)["Description"].tolist()
compare_products = st.multiselect(
    "Select products to compare",
    options=avail_products,
    default=avail_products[:3],
    max_selections=5,
    key="prod_compare",
)
if compare_products:
    fig = product_comparison_lines(mp, compare_products, height=420)
    st.plotly_chart(fig, use_container_width=True, key="prod_compare_chart")

# ── Product Drill-Down ─────────────────────────────────────────
render_section_header("🔍", "Product Deep Dive")
selected_product = st.selectbox("Select a product", products_df["Description"].head(30).tolist(), key="prod_drilldown")

if selected_product:
    mp_product = mp[mp["Description"] == selected_product]
    prod_total = float(products_df[products_df["Description"] == selected_product]["Revenue"].sum())
    prod_share = (prod_total / total_rev * 100) if total_rev > 0 else 0
    prod_rank = list(products_df["Description"]).index(selected_product) + 1 if selected_product in products_df["Description"].values else "N/A"

    d_cols = st.columns(4)
    with d_cols[0]:
        render_kpi_card("Revenue", prod_total, selected_product[:20], is_currency=True)
    with d_cols[1]:
        render_kpi_card("Share", f"{prod_share:.2f}%", "Of total revenue")
    with d_cols[2]:
        render_kpi_card("Rank", f"#{prod_rank}", f"Out of {total_products}")
    with d_cols[3]:
        best_month = mp_product.loc[mp_product["Revenue"].idxmax(), "YearMonth"] if not mp_product.empty else "N/A"
        render_kpi_card("Best Month", best_month, "Peak revenue period")

    if not mp_product.empty:
        fig = product_comparison_lines(mp, [selected_product], f"{selected_product[:40]} — Monthly Trend", 350)
        st.plotly_chart(fig, use_container_width=True, key="prod_drilldown_chart")

# ── Ranking Table ──────────────────────────────────────────────
render_section_header("📋", "Product Ranking Table")
display = compute_product_shares(products_df.head(30)).copy()
display["Revenue (£)"] = display["Revenue"].apply(lambda x: f"£{x:,.2f}")
display["Share"] = display["Share_Pct"].apply(lambda x: f"{x:.2f}%")
display.insert(0, "Rank", range(1, len(display) + 1))
st.dataframe(display[["Rank", "Description", "Revenue (£)", "Share"]], use_container_width=True, hide_index=True, height=400)

csv = products_df[["Description", "Revenue"]].to_csv(index=False)
st.download_button("📥 Download Product Data (CSV)", csv, "product_analysis.csv", "text/csv", key="prod_download")

render_app_footer()
