"""CourtIQ Formatting & Streamlit Design System.

Provides consistent styling, cards, typography, and badges across all pages.
"""

from typing import Any, Optional
import streamlit as st


def apply_custom_css() -> None:
    """Inject CourtIQ custom CSS for high-quality sports analytics UI."""
    custom_css = """
    <style>
        /* Import clean modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Top header card styling */
        .courtiq-header-banner {
            background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1976d2 100%);
            color: #ffffff;
            padding: 1.8rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 14px rgba(13, 71, 161, 0.15);
        }
        .courtiq-header-banner h1 {
            color: #ffffff !important;
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0;
            padding: 0;
        }
        .courtiq-header-banner p {
            color: #e3f2fd !important;
            font-size: 1.05rem;
            margin-top: 0.5rem;
            margin-bottom: 0;
        }

        /* KPI Metric Cards */
        .courtiq-kpi-card {
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin-bottom: 1rem;
        }
        .courtiq-kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border-color: #1976d2;
        }
        .courtiq-kpi-title {
            color: #546e7a;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }
        .courtiq-kpi-value {
            color: #102a43;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .courtiq-kpi-sub {
            color: #78909c;
            font-size: 0.8rem;
            margin-top: 0.3rem;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 4px;
            text-transform: uppercase;
        }
        .badge-primary { background-color: #e3f2fd; color: #0d47a1; }
        .badge-success { background-color: #e8f5e9; color: #1b5e20; }
        .badge-warning { background-color: #fff3e0; color: #e65100; }
        .badge-info { background-color: #e0f2f1; color: #004d40; }

        /* Section dividers */
        .section-header {
            border-bottom: 2px solid #eceff1;
            padding-bottom: 0.5rem;
            margin-top: 1.5rem;
            margin-bottom: 1.2rem;
            color: #102a43;
            font-weight: 600;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_metric_card(title: str, value: Any, subtext: Optional[str] = None) -> None:
    """Render a styled KPI card in Streamlit."""
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
    """Render a clean section header."""
    st.markdown(f'<h3 class="section-header">{title}</h3>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)
