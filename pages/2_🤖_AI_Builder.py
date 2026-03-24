"""
🤖 AI Dashboard Builder
Natural language → Parsed Spec → Grounding Verification → Power BI Artifact.
"""
import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.styles import get_custom_css
from ui.components import (
    render_section_header, render_kpi_card, render_badge, render_insight_card,
    render_build_step, render_empty_state, render_app_footer, render_trust_badges,
)
from services.ai_engine import parse_user_query, get_sample_prompts
from services.builder import build_dashboard
from services.data_loader import load_metadata, load_country_revenue, load_month_country
from ui.charts import monthly_revenue_line, top_countries_bar, top_products_bar, country_comparison_lines

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ── Init session state ─────────────────────────────────────────
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None
if "build_result" not in st.session_state:
    st.session_state.build_result = None
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "build_history" not in st.session_state:
    st.session_state.build_history = []

# ── Header ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner" style="padding: 1.5rem 2rem;">
    <h1 style="font-size: 1.8rem;">🤖 AI Dashboard Builder</h1>
    <div class="hero-subtitle">Describe what you want — the system interprets, validates, and builds.</div>
    <div class="hero-desc">Natural language → Structured Spec → Grounding Check → Deterministic PBIP Generation</div>
</div>
""", unsafe_allow_html=True)

render_trust_badges()

# ── Query Input ────────────────────────────────────────────────
render_section_header("💬", "Natural Language Query")

user_query = st.text_area(
    "Describe the dashboard you want to generate",
    value=st.session_state.last_query,
    height=100,
    placeholder="e.g., Show me France sales performance for March 2011 with top products and monthly trend",
    key="ai_query_input",
)

# Sample prompt chips
st.markdown("**Try an example:**")
sample_cols = st.columns(4)
samples = get_sample_prompts()
for i, sample in enumerate(samples[:8]):
    with sample_cols[i % 4]:
        if st.button(f"💡 {sample[:45]}…" if len(sample) > 45 else f"💡 {sample}", key=f"sample_{i}", use_container_width=True):
            st.session_state.last_query = sample
            del st.session_state["ai_query_input"]
            st.rerun()

# Action buttons
btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 1])
with btn_col1:
    parse_clicked = st.button("🔍 Parse & Validate", use_container_width=True, type="primary")
with btn_col2:
    generate_clicked = st.button("⚡ Generate PBIP Dashboard", use_container_width=True,
                                  disabled=not (st.session_state.ai_result and st.session_state.ai_result.get("success")))
with btn_col3:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.ai_result = None
        st.session_state.build_result = None
        st.session_state.last_query = ""
        del st.session_state["ai_query_input"]
        st.rerun()

# ── Parse Query ────────────────────────────────────────────────
if parse_clicked and user_query.strip():
    st.session_state.last_query = user_query
    with st.spinner("🔮 Calling Gemini and validating..."):
        try:
            result = parse_user_query(user_query.strip())
            st.session_state.ai_result = result
            st.session_state.build_result = None
        except Exception as e:
            st.session_state.ai_result = {"success": False, "error": str(e)}
elif parse_clicked:
    st.warning("Please enter a query first.")

# ── Display Results ────────────────────────────────────────────
result = st.session_state.ai_result

if result:
    st.divider()

    if result.get("error") and not result.get("spec_dict"):
        st.error(f"❌ **Error:** {result['error']}")
        with st.expander("🔧 Technical Details"):
            st.code(result.get("error", ""), language="text")
    else:
        # Layout: Interpretation | Grounding | Visuals
        col_spec, col_ground = st.columns([3, 2])

        with col_spec:
            render_section_header("🧠", "Parsed Interpretation")
            spec = result.get("spec_dict", {})

            # Status badge
            if result.get("success"):
                st.markdown(render_badge("✓ Validation Passed", "success"), unsafe_allow_html=True)
            elif result.get("validation_errors"):
                st.markdown(render_badge("⚠ Validation Issues", "warning"), unsafe_allow_html=True)
                for err in result["validation_errors"]:
                    st.warning(err)

            # Dashboard title
            st.markdown(f"**Dashboard Title:** `{spec.get('dashboard_title', 'N/A')}`")

            # Filters
            filters = spec.get("filters", {})
            fym = filters.get("YearMonth", [])
            fc = filters.get("Country", [])
            st.markdown(f"**Selected Months:** {', '.join(fym) if fym else 'All'}")
            st.markdown(f"**Selected Countries:** {', '.join(fc) if fc else 'All'}")

            # Visual Slots
            render_section_header("🎨", "Visual Slots")
            visuals = spec.get("visuals_config", {})
            slot_cols = st.columns(4)
            slot_names = {
                "slot_kpi_cards": ("📊", "KPI Cards"),
                "slot_trend": ("📈", "Trend Chart"),
                "slot_top_countries": ("🌍", "Top Countries"),
                "slot_top_products": ("📦", "Top Products"),
            }
            for i, (slot_key, (icon, label)) in enumerate(slot_names.items()):
                slot_data = visuals.get(slot_key, {})
                is_visible = slot_data.get("visible", False) if isinstance(slot_data, dict) else False
                with slot_cols[i]:
                    variant = "success" if is_visible else "neutral"
                    status = "Active" if is_visible else "Hidden"
                    st.markdown(f"""
                    <div class="kpi-card" style="padding: 0.8rem;">
                        <div style="font-size: 1.5rem;">{icon}</div>
                        <div class="kpi-label">{label}</div>
                        {render_badge(status, variant)}
                    </div>
                    """, unsafe_allow_html=True)

        with col_ground:
            render_section_header("🔒", "Grounding Verification")
            report = result.get("grounding_report", {})

            if report:
                all_grounded = report.get("all_grounded", False)
                if all_grounded:
                    st.markdown(render_badge("✓ All Values Grounded", "success"), unsafe_allow_html=True)
                else:
                    st.markdown(render_badge("⚠ Ungrounded Values Detected", "warning"), unsafe_allow_html=True)

                st.markdown(f"**Metadata Coverage:** {report.get('allowed_yearmonths_count', 0)} months, {report.get('allowed_countries_count', 0)} countries")

                if report.get("matched_yearmonths"):
                    st.markdown(f"✅ **Matched Months:** {', '.join(report['matched_yearmonths'])}")
                if report.get("unmatched_yearmonths"):
                    st.markdown(f"❌ **Unmatched Months:** {', '.join(report['unmatched_yearmonths'])}")
                if report.get("matched_countries"):
                    st.markdown(f"✅ **Matched Countries:** {', '.join(report['matched_countries'])}")
                if report.get("unmatched_countries"):
                    st.markdown(f"❌ **Unmatched Countries:** {', '.join(report['unmatched_countries'])}")

                render_insight_card(
                    "Grounding ensures that the LLM's output references only values present in the processed metadata. "
                    "Unmatched values are rejected to prevent hallucinated filters from reaching the builder."
                )
            else:
                st.info("Grounding report not available.")

        # JSON Spec Viewer
        render_section_header("📄", "Dashboard Specification (JSON)")
        with st.expander("View raw DashboardSpec JSON", expanded=False):
            st.code(json.dumps(spec, indent=2), language="json")

        # ── Lightweight Preview ────────────────────────────────
        render_section_header("👁️", "Filtered Data Preview")
        st.caption("This shows a Streamlit-side preview of the data that matches the parsed filters. The actual output is a Power BI Project artifact.")

        preview_ym = filters.get("YearMonth", [])
        preview_countries = filters.get("Country", [])

        mc_data = load_month_country()
        if preview_ym:
            mc_data = mc_data[mc_data["YearMonth"].isin(preview_ym)]
        if preview_countries:
            mc_data = mc_data[mc_data["Country"].isin(preview_countries)]

        # Derive monthly revenue from the (already filtered) month-country data
        monthly = mc_data.groupby("YearMonth")["Revenue"].sum().reset_index().sort_values("YearMonth")

        prev_col1, prev_col2 = st.columns(2)
        with prev_col1:
            if not mc_data.empty:
                if preview_countries and len(preview_countries) >= 1:
                    fig = country_comparison_lines(mc_data, preview_countries, "Revenue by Country", 300)
                else:
                    fig = monthly_revenue_line(monthly, "Revenue for Selected Period", 300)
                st.plotly_chart(fig, use_container_width=True, key="ai_preview_trend")
            else:
                st.info("No monthly data for selected filters.")
        with prev_col2:
            if not mc_data.empty:
                country_agg = mc_data.groupby("Country")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
                fig = top_countries_bar(country_agg, 8, "Countries for Selected Period", 300)
                st.plotly_chart(fig, use_container_width=True, key="ai_preview_countries")
            else:
                st.info("No country data for selected filters.")

elif not parse_clicked:
    render_empty_state("🤖", "No query submitted yet", "Enter a natural language request above and click 'Parse & Validate' to begin.")

# ── Generate Dashboard ─────────────────────────────────────────
if generate_clicked and result and result.get("success") and result.get("spec_dict"):
    st.divider()
    render_section_header("⚙️", "Building Power BI Project Artifact")

    with st.spinner("🔨 Generating deterministic dashboard..."):
        build_result = build_dashboard(result["spec_dict"])
        st.session_state.build_result = build_result
        st.session_state.build_history.append(build_result)

# ── Build Status ───────────────────────────────────────────────
build_result = st.session_state.build_result
if build_result:
    st.divider()
    render_section_header("📦", "Build Result")

    if build_result.get("success"):
        st.markdown(render_badge("✓ Build Successful", "success"), unsafe_allow_html=True)
    else:
        st.markdown(render_badge("✗ Build Failed", "error"), unsafe_allow_html=True)

    st.markdown(f"**Dashboard:** `{build_result.get('dashboard_title', 'N/A')}`")
    st.markdown(f"**Build ID:** `{build_result.get('build_id', 'N/A')}`")
    st.markdown(f"**Output Path:** `{build_result.get('output_path', 'N/A')}`")
    st.markdown(f"**Timestamp:** {build_result.get('timestamp', 'N/A')}")

    render_section_header("📋", "Build Pipeline Steps")
    for step in build_result.get("steps", []):
        render_build_step(step["step"], step["status"], step.get("detail", ""))

    if build_result.get("error"):
        st.error(f"Error: {build_result['error']}")

render_app_footer()
