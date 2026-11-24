"""CourtIQ Formatting & Streamlit Design System.

Provides modern dark-mode glassmorphic aesthetics, cards, typography,
and bespoke navigation across the CourtIQ sports intelligence platform.
"""

from typing import Any, Optional
import streamlit as st


def apply_custom_css() -> None:
    """Inject CourtIQ custom CSS for an enterprise-grade sports analytics UI."""
    custom_css = """
    <style>
        /* Import Inter & Outfit modern typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hide Streamlit default Deploy button, toolbar, and footer */
        [data-testid="stToolbar"] {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
        footer {
            visibility: hidden !important;
        }

        /* Top Hero Header Banner */
        .courtiq-header-banner {
            background: radial-gradient(circle at 10% 20%, rgba(37, 99, 235, 0.22) 0%, transparent 45%),
                        radial-gradient(circle at 90% 80%, rgba(14, 165, 233, 0.18) 0%, transparent 45%),
                        linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 16px;
            padding: 2rem 2.2rem;
            margin-bottom: 1.8rem;
            box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.25);
            position: relative;
            overflow: hidden;
        }
        .courtiq-header-banner::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 2px;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #38bdf8);
        }
        .courtiq-header-banner h1 {
            color: #ffffff !important;
            font-family: 'Outfit', sans-serif !important;
            font-size: 2.3rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            padding: 0 !important;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }
        .courtiq-header-banner p {
            color: #94a3b8 !important;
            font-size: 1.05rem !important;
            margin-top: 0.6rem !important;
            margin-bottom: 0 !important;
            max-width: 800px;
            line-height: 1.5;
        }

        /* Top Navigation Bar */
        .courtiq-nav-bar {
            display: flex;
            gap: 0.8rem;
            margin-bottom: 1.5rem;
            padding: 0.5rem 0.8rem;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        .courtiq-nav-pill {
            padding: 0.45rem 1rem;
            border-radius: 8px;
            font-size: 0.88rem;
            font-weight: 500;
            color: #94a3b8;
            text-decoration: none;
            transition: all 0.2s ease;
        }
        .courtiq-nav-pill:hover {
            color: #f8fafc;
            background: rgba(255, 255, 255, 0.05);
        }
        .courtiq-nav-pill.active {
            color: #ffffff;
            background: linear-gradient(135deg, #0284c7, #2563eb);
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
        }

        /* Modern Dark Glassmorphic KPI Metric Cards */
        .courtiq-kpi-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.85));
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 14px;
            padding: 1.3rem 1.4rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(12px);
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        }
        .courtiq-kpi-card:hover {
            transform: translateY(-3px);
            border-color: rgba(56, 189, 248, 0.45);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 0 16px rgba(56, 189, 248, 0.15);
        }
        .courtiq-kpi-title {
            color: #94a3b8;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }
        .courtiq-kpi-value {
            color: #f8fafc;
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }
        .courtiq-kpi-sub {
            color: #64748b;
            font-size: 0.82rem;
            margin-top: 0.35rem;
            font-weight: 500;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            font-size: 0.72rem;
            font-weight: 700;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .badge-pro {
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(99, 102, 241, 0.25));
            border: 1px solid rgba(56, 189, 248, 0.4);
            color: #38bdf8;
        }
        .badge-success {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #34d399;
        }
        .badge-warning {
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.35);
            color: #fbbf24;
        }
        .badge-info {
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38bdf8;
        }

        /* Section Headers */
        .section-header {
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 0.6rem;
            margin-top: 2rem;
            margin-bottom: 1.2rem;
            color: #f1f5f9;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 1.35rem;
            letter-spacing: -0.01em;
        }

        /* Streamlit Buttons Overrides */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
            color: #ffffff !important;
            border-radius: 9px !important;
            font-weight: 600 !important;
            padding: 0.55rem 1.2rem !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 6px 22px rgba(37, 99, 235, 0.5) !important;
            transform: translateY(-1px) !important;
            border-color: #38bdf8 !important;
        }
        div.stButton > button[kind="secondary"] {
            background: rgba(30, 41, 59, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #e2e8f0 !important;
            border-radius: 9px !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button[kind="secondary"]:hover {
            background: rgba(51, 65, 85, 0.7) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
        }

        /* Streamlit Tabs Customization */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(15, 23, 42, 0.5);
            padding: 6px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 8px 16px;
            color: #94a3b8;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(30, 41, 59, 0.9) !important;
            color: #38bdf8 !important;
            font-weight: 600 !important;
        }

        /* Streamlit Alerts / Info / Warning refinement */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border-width: 1px !important;
            backdrop-filter: blur(8px) !important;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_metric_card(title: str, value: Any, subtext: Optional[str] = None) -> None:
    """Render a modern dark-mode glassmorphic KPI card in Streamlit."""
    sub_html = f'<div class="courtiq-kpi-sub">{subtext}</div>' if subtext else ""
    html = f"""
    <div class="courtiq-kpi-card">
        <div class="courtiq-kpi-title">{title}</div>
        <div class="courtiq-kpi-value">{value}</div>
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_badge(text: str, badge_type: str = "primary") -> str:
    """Return HTML string for a colored badge."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'


def render_section_header(title: str, subtitle: Optional[str] = None) -> None:
    """Render a clean section header with modern typography."""
    st.markdown(f'<h3 class="section-header">{title}</h3>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)
