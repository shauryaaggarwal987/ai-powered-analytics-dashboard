"""
AI-Powered Analytics Dashboard
Main entry point — multipage Streamlit application.
"""
import streamlit as st
import sys
import os

# Ensure project root on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="AI Analytics Dashboard",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.styles import get_custom_css
from ui.components import render_trust_badges
from services.data_loader import load_metadata

# ── Inject Custom CSS ──────────────────────────────────────────
st.markdown(get_custom_css(), unsafe_allow_html=True)


# ── Sidebar: Global Filters ───────────────────────────────────
def setup_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 0.8rem 0 0.5rem 0;">
            <span style="font-size: 2rem;">🔮</span>
            <div style="font-size: 1.1rem; font-weight: 700; color: #c4b5fd; margin-top: 0.2rem;">AI Analytics</div>
            <div style="font-size: 0.7rem; color: #64748b;">Grounded · Deterministic · Intelligent</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-title">Global Filters</div>', unsafe_allow_html=True)

        metadata = load_metadata()
        all_yearmonths = metadata.get("allowed_yearmonths", [])
        all_countries = metadata.get("allowed_countries", [])

        selected_yearmonths = st.multiselect(
            "📅 Year-Month",
            options=all_yearmonths,
            default=[],
            key="global_yearmonths",
            help="Filter all charts by specific months",
        )

        selected_countries = st.multiselect(
            "🌍 Country",
            options=all_countries,
            default=[],
            key="global_countries",
            help="Filter all charts by specific countries",
        )

        top_n = st.slider("🔢 Top N Items", min_value=5, max_value=30, value=10, key="global_top_n")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state["global_yearmonths"] = []
                st.session_state["global_countries"] = []
                st.session_state["global_top_n"] = 10
                st.rerun()
        with col2:
            if st.button("📊 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

        st.markdown('<div class="sidebar-section-title">System Status</div>', unsafe_allow_html=True)

        files_status = {
            "Metadata": os.path.exists(os.path.join(os.path.dirname(__file__), "data", "processed", "metadata.json")),
            "Monthly Data": os.path.exists(os.path.join(os.path.dirname(__file__), "data", "processed", "monthly_revenue.csv")),
            "Country Data": os.path.exists(os.path.join(os.path.dirname(__file__), "data", "processed", "country_revenue.csv")),
            "Products Data": os.path.exists(os.path.join(os.path.dirname(__file__), "data", "processed", "top_products.csv")),
        }

        for name, exists in files_status.items():
            icon = "🟢" if exists else "🔴"
            st.markdown(f"<span style='font-size:0.78rem; color: #94a3b8;'>{icon} {name}</span>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-title">Trust & Privacy</div>', unsafe_allow_html=True)
        render_trust_badges()


# ── Page Navigation ────────────────────────────────────────────
setup_sidebar()

overview_page = st.Page("pages/1_📊_Overview.py", title="Overview", icon="📊", default=True)
ai_builder_page = st.Page("pages/2_🤖_AI_Builder.py", title="AI Builder", icon="🤖")
trends_page = st.Page("pages/3_📈_Trends.py", title="Trends", icon="📈")
geography_page = st.Page("pages/4_🌍_Geography.py", title="Geography", icon="🌍")
products_page = st.Page("pages/5_📦_Products.py", title="Products", icon="📦")
metadata_page = st.Page("pages/6_🔍_Metadata.py", title="Data & Grounding", icon="🔍")
export_page = st.Page("pages/7_📁_Export.py", title="Export Center", icon="📁")
architecture_page = st.Page("pages/8_🏗️_Architecture.py", title="Architecture", icon="🏗️")

pg = st.navigation({
    "Analytics": [overview_page, trends_page, geography_page, products_page],
    "AI & Build": [ai_builder_page, export_page],
    "System": [metadata_page, architecture_page],
})

pg.run()
