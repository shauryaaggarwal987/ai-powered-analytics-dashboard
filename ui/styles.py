"""
Custom CSS Styles
Premium dark-theme styling for the analytics dashboard.
"""


def get_custom_css() -> str:
    """Return the complete custom CSS for the dashboard."""
    return """
<style>
    /* ===== Global ===== */
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1419 0%, #1a1f2e 100%); }
    h1, h2, h3 { letter-spacing: -0.02em; }

    /* ===== Hero Banner ===== */
    .hero-banner {
        background: linear-gradient(135deg, #1a1f2e 0%, #2d1b69 50%, #1a3a5c 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(108, 99, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(108,99,255,0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-banner h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        color: #a5b4fc;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
        font-weight: 400;
    }
    .hero-desc {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* ===== KPI Cards ===== */
    .kpi-card {
        background: linear-gradient(135deg, #1e2433 0%, #232b3e 100%);
        border: 1px solid rgba(108, 99, 255, 0.15);
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(108, 99, 255, 0.4);
    }
    .kpi-label {
        color: #94a3b8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        color: #f1f5f9;
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .kpi-sub {
        color: #64748b;
        font-size: 0.72rem;
        margin-top: 0.25rem;
    }

    /* ===== Section Headers ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(108, 99, 255, 0.15);
    }
    .section-header h3 {
        margin: 0;
        font-size: 1.15rem;
        font-weight: 600;
        color: #e2e8f0;
    }
    .section-icon {
        font-size: 1.3rem;
    }

    /* ===== Status Badges ===== */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .badge-success { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-warning { background: rgba(251, 191, 36, 0.15); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.3); }
    .badge-error { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-info { background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); }
    .badge-neutral { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.2); }

    /* ===== Insight Cards ===== */
    .insight-card {
        background: rgba(30, 36, 51, 0.7);
        border: 1px solid rgba(108, 99, 255, 0.1);
        border-left: 3px solid #6C63FF;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        color: #cbd5e1;
        line-height: 1.5;
    }
    .insight-card strong { color: #a5b4fc; }

    /* ===== Architecture Cards ===== */
    .arch-card {
        background: linear-gradient(135deg, #1e2433 0%, #1a2038 100%);
        border: 1px solid rgba(108, 99, 255, 0.12);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .arch-card h4 {
        color: #a5b4fc;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    .arch-card p {
        color: #94a3b8;
        font-size: 0.88rem;
        line-height: 1.55;
        margin: 0;
    }

    /* ===== Build Steps ===== */
    .build-step {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.5rem 0.8rem;
        border-left: 2px solid #334155;
        margin: 0.3rem 0;
        font-size: 0.85rem;
    }
    .build-step.step-success { border-left-color: #4ade80; }
    .build-step.step-error { border-left-color: #f87171; }
    .build-step.step-warning { border-left-color: #fbbf24; }
    .build-step.step-running { border-left-color: #6C63FF; }

    /* ===== Empty State ===== */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #64748b;
    }
    .empty-state .empty-icon {
        font-size: 3rem;
        margin-bottom: 0.8rem;
        opacity: 0.5;
    }
    .empty-state h4 {
        color: #94a3b8;
        margin-bottom: 0.4rem;
    }
    .empty-state p {
        font-size: 0.88rem;
    }

    /* ===== Trust Badges ===== */
    .trust-badges {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin: 0.8rem 0;
    }
    .trust-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.85rem;
        background: rgba(108, 99, 255, 0.08);
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 20px;
        font-size: 0.75rem;
        color: #c4b5fd;
        font-weight: 500;
    }

    /* ===== Prompt Chips ===== */
    .prompt-chip {
        display: inline-block;
        padding: 0.4rem 0.9rem;
        background: rgba(108, 99, 255, 0.08);
        border: 1px solid rgba(108, 99, 255, 0.25);
        border-radius: 20px;
        font-size: 0.8rem;
        color: #c4b5fd;
        cursor: pointer;
        margin: 0.2rem;
        transition: all 0.2s ease;
    }
    .prompt-chip:hover {
        background: rgba(108, 99, 255, 0.18);
        border-color: rgba(108, 99, 255, 0.45);
    }

    /* ===== Sidebar Enhancements ===== */
    .sidebar-section-title {
        color: #94a3b8;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 700;
        margin-top: 1.2rem;
        margin-bottom: 0.4rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid rgba(108, 99, 255, 0.1);
    }

    /* ===== Footer ===== */
    .app-footer {
        margin-top: 3rem;
        padding: 1.5rem 0;
        border-top: 1px solid rgba(108, 99, 255, 0.1);
        text-align: center;
        color: #475569;
        font-size: 0.78rem;
    }

    /* ===== Data Table Enhancements ===== */
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* ===== Tabs ===== */
    .stTabs [data-baseweb="tab-list"] { gap: 1.5rem; }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.88rem;
        font-weight: 500;
        padding: 0.6rem 0;
    }
</style>
"""
