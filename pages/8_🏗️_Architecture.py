"""
🏗️ Architecture & System Explainability
Explains the system architecture, trust posture, and design philosophy.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui.styles import get_custom_css
from ui.components import render_section_header, render_architecture_card, render_trust_badges, render_app_footer, render_insight_card

st.markdown(get_custom_css(), unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner" style="padding: 1.5rem 2rem;">
    <h1 style="font-size: 1.6rem;">🏗️ System Architecture</h1>
    <div class="hero-subtitle">How AI-Powered Analytics Dashboard works — from data to deterministic dashboard generation.</div>
</div>
""", unsafe_allow_html=True)

render_trust_badges()

# ── System Overview ────────────────────────────────────────────
render_section_header("🔮", "System Overview")
st.markdown("""
The **AI-Powered Analytics Dashboard** is a hybrid intelligence system that bridges natural language analytics requests
with deterministic Power BI Project generation. It is designed to be **trustworthy**, **transparent**, and **grounded** — 
the LLM acts as a semantic interpreter, not a dashboard generator.
""")

# ── End-to-End Flow ────────────────────────────────────────────
render_section_header("🔄", "End-to-End Data Flow")

flow_cols = st.columns(5)
flow_steps = [
    ("1️⃣", "Raw Data", "Online Retail II CSV → Cleaning → Revenue computation → Processed KPI tables"),
    ("2️⃣", "Metadata", "Extract allowed YearMonth + Country values → metadata.json for LLM grounding"),
    ("3️⃣", "LLM Intent", "User query + metadata context → Gemini → Structured DashboardSpec JSON"),
    ("4️⃣", "Validation", "Pydantic model validates spec against metadata → Reject invalid values"),
    ("5️⃣", "Build", "Clone PBIP template → Apply spec (title, filters, slots) → Output artifact"),
]

for i, (num, title, desc) in enumerate(flow_steps):
    with flow_cols[i]:
        st.markdown(f"""
        <div class="arch-card" style="text-align:center; min-height: 200px;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{num}</div>
            <h4 style="margin-bottom: 0.5rem;">{title}</h4>
            <p style="font-size: 0.8rem;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ── Component Deep Dives ───────────────────────────────────────
render_section_header("📦", "Component Architecture")

render_architecture_card(
    "📊", "Analytics Pipeline",
    "The analytics layer processes raw Online Retail II transaction data through a series of deterministic Python scripts: "
    "cleaning_v1.py removes invalid quantities/prices and computes Revenue; monthly_trends.py, country_contribution.py, "
    "top_products.py, month_country.py, and month_product.py generate aggregated KPI tables stored as CSVs in data/processed/."
)

render_architecture_card(
    "📋", "Metadata & Grounding Layer",
    "allowed_values.py extracts the unique YearMonth and Country values from processed tables and stores them in metadata.json. "
    "This file serves as the single source of truth for what the LLM is allowed to reference. It prevents hallucinated filter "
    "values and ensures every dashboard specification is anchored in real data."
)

render_architecture_card(
    "🤖", "LLM Semantic Layer (Gemini)",
    "The Google Gemini API receives a carefully constructed prompt containing: (1) the user's natural language request, "
    "(2) the list of allowed values from metadata.json, and (3) the JSON Schema of DashboardSpec. The model's role is strictly "
    "semantic interpretation — translating intent into a structured configuration. Raw transactional data is never sent to Gemini."
)

render_architecture_card(
    "✅", "Pydantic Validation",
    "dashboard_spec.py defines a Pydantic BaseModel with a model_validator that loads metadata.json and checks every filter "
    "value against the allowed sets. If the LLM returns a YearMonth or Country not in the grounded metadata, a ValidationError "
    "is raised immediately — preventing invalid configurations from reaching the builder."
)

render_architecture_card(
    "⚙️", "Deterministic Template Builder",
    "The builder does not generate Power BI internals from scratch. Instead, it clones a pre-built .pbip template folder "
    "and modifies targeted JSON objects: the dashboard title (using a marker like __DASHBOARD_TITLE__), filter definitions, "
    "and visual slot visibility flags. This ensures structural correctness and avoids the fragility of LLM-generated BI files."
)

render_architecture_card(
    "🖥️", "Streamlit Orchestration UI",
    "The Streamlit app serves as the interactive frontend: it loads processed data, renders analytics charts, accepts "
    "natural language queries, displays parsed specs and grounding reports, triggers the build pipeline, and delivers the "
    "output artifact. It is the orchestration layer — not the final dashboard itself."
)

# ── Trust & Privacy ────────────────────────────────────────────
render_section_header("🔒", "Trust & Privacy Posture")

priv_col1, priv_col2 = st.columns(2)
with priv_col1:
    render_architecture_card(
        "🏠", "Local-First Processing",
        "All data processing — cleaning, aggregation, KPI computation — happens locally on the user's machine. "
        "No raw transactional records leave the local environment."
    )
    render_architecture_card(
        "🚫", "No Raw Data to LLM",
        "Gemini receives only: (1) allowed filter value lists, (2) the DashboardSpec JSON Schema, and (3) the user's "
        "natural language query. Customer IDs, invoice details, and individual transactions are never transmitted."
    )

with priv_col2:
    render_architecture_card(
        "🛡️", "Validated Outputs Only",
        "Every LLM output passes through Pydantic validation before any action is taken. Invalid or hallucinated "
        "values are caught and rejected with clear error messages."
    )
    render_architecture_card(
        "📐", "Template-Driven Generation",
        "Power BI artifacts are generated by modifying existing template files, not by having the LLM write "
        "proprietary BI markup. This eliminates the risk of malformed or insecure dashboard definitions."
    )

# ── Why This Architecture ─────────────────────────────────────
render_section_header("💡", "Why This Architecture?")

render_insight_card(
    "Most AI dashboard tools allow the LLM to directly generate dashboard internals — which risks hallucinated data, "
    "broken visualizations, and security concerns. This system instead treats the LLM as a <strong>semantic translator</strong> "
    "that maps user intent to a <strong>constrained specification</strong>, which is then applied <strong>deterministically</strong> "
    "to a known-good template. The result is predictable, safe, and easily auditable."
)

# ── Technology Stack ───────────────────────────────────────────
render_section_header("🔧", "Technology Stack")

tech_cols = st.columns(3)
with tech_cols[0]:
    st.markdown("**Frontend & UI**")
    st.markdown("- Streamlit (multipage app)")
    st.markdown("- Plotly (interactive charts)")
    st.markdown("- Custom CSS (premium styling)")

with tech_cols[1]:
    st.markdown("**Backend & Data**")
    st.markdown("- Python + Pandas")
    st.markdown("- Pydantic (validation)")
    st.markdown("- JSON (metadata + specs)")

with tech_cols[2]:
    st.markdown("**AI & Output**")
    st.markdown("- Google Gemini API")
    st.markdown("- Power BI Project (.pbip)")
    st.markdown("- Template-based generation")

# ── Extension Points ──────────────────────────────────────────
render_section_header("🔌", "Extension Points")
st.markdown("""
This architecture is designed for future expansion:

- **New Visual Slots** — Add more visual types in `template_map.json` and the template `report.json`
- **New Processed Tables** — Create additional analytics scripts and register them in the data loader
- **Additional Metrics** — Extend the capabilities metadata with new metric types (e.g., quantity, margin)
- **New Filters** — Add dimensions like Product or Customer segment to metadata.json
- **FastAPI Backend** — Separate the API layer from the UI for microservice deployment
- **Authentication** — Add user authentication for multi-user access
- **Streaming LLM** — Use Gemini streaming for real-time intent parsing feedback
""")

render_app_footer()
