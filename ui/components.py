"""
Reusable UI Components
Helper functions for rendering premium UI elements.
"""
import streamlit as st
from services.metrics import format_currency, format_number


def render_hero_banner(title: str, subtitle: str, description: str = ""):
    """Render the premium hero banner."""
    desc_html = f'<div class="hero-desc">{description}</div>' if description else ""
    st.markdown(f"""
    <div class="hero-banner">
        <h1>{title}</h1>
        <div class="hero-subtitle">{subtitle}</div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(label: str, value, sub: str = "", is_currency: bool = False):
    """Render a single KPI metric card."""
    if is_currency and isinstance(value, (int, float)):
        display_value = format_currency(value)
    elif isinstance(value, (int, float)):
        display_value = format_number(value)
    else:
        display_value = str(value)
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{display_value}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_section_header(icon: str, title: str):
    """Render a styled section header."""
    st.markdown(f"""
    <div class="section-header">
        <span class="section-icon">{icon}</span>
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)


def render_badge(text: str, variant: str = "info"):
    """Render a status badge. Variants: success, warning, error, info, neutral."""
    return f'<span class="badge badge-{variant}">{text}</span>'


def render_insight_card(text: str):
    """Render a narrative insight card."""
    st.markdown(f'<div class="insight-card">{text}</div>', unsafe_allow_html=True)


def render_empty_state(icon: str, title: str, message: str):
    """Render a polished empty state."""
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <h4>{title}</h4>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)


def render_trust_badges():
    """Render the trust/architecture badges."""
    st.markdown("""
    <div class="trust-badges">
        <span class="trust-badge">🔒 Local Data Processing</span>
        <span class="trust-badge">🤖 LLM-Grounded</span>
        <span class="trust-badge">⚙️ Deterministic Builder</span>
        <span class="trust-badge">✅ Pydantic Validated</span>
    </div>
    """, unsafe_allow_html=True)


def render_architecture_card(icon: str, title: str, description: str):
    """Render an architecture explanation card."""
    st.markdown(f"""
    <div class="arch-card">
        <h4>{icon} {title}</h4>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)


def render_build_step(step_name: str, status: str, detail: str):
    """Render a single build pipeline step."""
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "running": "🔄"}
    icon = icons.get(status, "⏳")
    st.markdown(f"""
    <div class="build-step step-{status}">
        <span>{icon}</span>
        <strong>{step_name}</strong>
        <span style="color: #64748b; margin-left: auto; font-size: 0.8rem;">{detail}</span>
    </div>
    """, unsafe_allow_html=True)


def render_filter_chips(yearmonths: list = None, countries: list = None):
    """Render active filter indicator chips."""
    chips = []
    if yearmonths:
        for ym in yearmonths[:5]:
            chips.append(f'<span class="badge badge-info">📅 {ym}</span>')
        if len(yearmonths) > 5:
            chips.append(f'<span class="badge badge-neutral">+{len(yearmonths)-5} more</span>')
    if countries:
        for c in countries[:3]:
            chips.append(f'<span class="badge badge-info">🌍 {c}</span>')
        if len(countries) > 3:
            chips.append(f'<span class="badge badge-neutral">+{len(countries)-3} more</span>')
    if chips:
        st.markdown(f'<div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.8rem;">{"".join(chips)}</div>', unsafe_allow_html=True)


def render_app_footer():
    """Render the application footer."""
    st.markdown("""
    <div class="app-footer">
        <strong>AI-Powered Analytics Dashboard</strong> · Deterministic Template Builder · LLM-Grounded · Local-First Processing<br/>
        Built with Streamlit · Plotly · Gemini · Pydantic
    </div>
    """, unsafe_allow_html=True)
