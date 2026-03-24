"""
📁 Build / Export / Artifact Center
Build history, artifact delivery, and audit trail.
"""
import streamlit as st
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.styles import get_custom_css
from ui.components import (
    render_section_header, render_kpi_card, render_build_step,
    render_empty_state, render_app_footer, render_badge,
)
from services.builder import get_build_history

st.markdown(get_custom_css(), unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner" style="padding: 1.2rem 1.5rem;">
    <h1 style="font-size: 1.6rem;">📁 Export & Artifact Center</h1>
    <div class="hero-subtitle">View build history, inspect generated artifacts, and download outputs.</div>
</div>
""", unsafe_allow_html=True)

# ── Session Build History ──────────────────────────────────────
session_builds = st.session_state.get("build_history", [])

render_section_header("⚡", "Current Session Builds")
if session_builds:
    k_cols = st.columns(3)
    with k_cols[0]:
        render_kpi_card("Session Builds", len(session_builds), "This session")
    with k_cols[1]:
        successful = sum(1 for b in session_builds if b.get("success"))
        render_kpi_card("Successful", successful, f"{len(session_builds) - successful} failed")
    with k_cols[2]:
        latest = session_builds[-1]
        render_kpi_card("Latest", latest.get("dashboard_title", "N/A")[:20], latest.get("timestamp", "")[:19])

    for i, build in enumerate(reversed(session_builds)):
        with st.expander(f"{'✅' if build.get('success') else '❌'} Build: {build.get('dashboard_title', 'Untitled')} — {build.get('timestamp', '')[:19]}", expanded=(i == 0)):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Build ID:** `{build.get('build_id', 'N/A')}`")
                st.markdown(f"**Output Path:** `{build.get('output_path', 'N/A')}`")
                st.markdown(f"**Timestamp:** {build.get('timestamp', 'N/A')}")
                filters = build.get("filters_applied", {})
                ym = filters.get("YearMonth", [])
                countries = filters.get("Country", [])
                st.markdown(f"**Months:** {', '.join(ym) if ym else 'All'}")
                st.markdown(f"**Countries:** {', '.join(countries) if countries else 'All'}")
            with col2:
                st.markdown("**Build Pipeline:**")
                for step in build.get("steps", []):
                    render_build_step(step["step"], step["status"], step.get("detail", ""))

            if build.get("error"):
                st.error(f"Error: {build['error']}")
else:
    render_empty_state("📦", "No builds in this session", "Go to the AI Builder page to generate a Power BI Project artifact.")

# ── Filesystem Build History ───────────────────────────────────
render_section_header("📚", "All Build Artifacts")
all_builds = get_build_history()

if all_builds:
    st.markdown(f"Found **{len(all_builds)}** artifacts in the output directory.")
    st.markdown("")

    # Table view
    table_data = []
    for b in all_builds:
        filters = b.get("filters", {})
        ym = ", ".join(filters.get("YearMonth", [])) or "All"
        countries = ", ".join(filters.get("Country", [])) or "All"
        table_data.append({
            "Build ID": b["build_id"],
            "Title": b["title"],
            "Months": ym,
            "Countries": countries,
            "Path": b["path"],
        })

    import pandas as pd
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True, height=350)

    # Detail expander for each
    render_section_header("🔍", "Artifact Details")
    selected_build = st.selectbox("Select an artifact to inspect", [b["build_id"] for b in all_builds], key="export_select")

    if selected_build:
        build_info = next((b for b in all_builds if b["build_id"] == selected_build), None)
        if build_info:
            st.markdown(f"**Title:** `{build_info['title']}`")
            st.markdown(f"**Path:** `{build_info['path']}`")

            # Try to load and show the spec
            spec_path = os.path.join(build_info["path"], "dashboard_spec.json")
            if os.path.exists(spec_path):
                with open(spec_path, "r") as f:
                    spec = json.load(f)
                with st.expander("View DashboardSpec JSON"):
                    st.code(json.dumps(spec, indent=2), language="json")

            # List files in the build directory
            if os.path.exists(build_info["path"]):
                st.markdown("**Files in artifact:**")
                for root, dirs, files in os.walk(build_info["path"]):
                    level = root.replace(build_info["path"], "").count(os.sep)
                    indent = "│  " * level
                    folder_name = os.path.basename(root)
                    if level == 0:
                        st.markdown(f"`📁 {folder_name}/`")
                    else:
                        st.markdown(f"`{indent}📁 {folder_name}/`")
                    for file in files:
                        st.markdown(f"`{indent}│  📄 {file}`")
else:
    render_empty_state("📁", "No artifacts found", "No build artifacts exist in the output directory. Generate a dashboard from the AI Builder page.")

# ── Architecture Note ──────────────────────────────────────────
render_section_header("ℹ️", "About Artifacts")
st.markdown("""
Each build artifact is a **Power BI Project (.pbip)** folder structure generated through deterministic template manipulation:

1. A pre-built Power BI template is cloned to a timestamped output folder
2. The validated DashboardSpec is applied — titles, filters, and visual slots are injected
3. The resulting folder can be opened directly in Power BI Desktop

> **Note:** The Streamlit app is the orchestration interface. The actual BI artifact is the `.pbip` output designed for Power BI Desktop.
""")

render_app_footer()
