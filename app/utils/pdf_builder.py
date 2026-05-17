"""
PDF report builder utility for GodaamX.

Transforms dashboard JSON data into a clean, structured PDF report
using fpdf2. Supports both SuperAdmin and Supplier dashboard layouts.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from typing import Any

from fpdf import FPDF


# ── Colour palette ──────────────────────────────────────────────────
_PRIMARY = (30, 58, 138)       # deep blue
_SECONDARY = (100, 116, 139)   # slate
_ACCENT = (14, 165, 233)       # sky-500
_WHITE = (255, 255, 255)
_LIGHT_BG = (241, 245, 249)    # slate-100
_DARK_TEXT = (15, 23, 42)       # slate-900
_BORDER = (203, 213, 225)      # slate-300

# ── Unicode → Latin-1 replacements ──────────────────────────────────
# Helvetica only supports Latin-1 (ISO 8859-1). Map common Unicode
# characters that may appear in data to safe ASCII/Latin-1 equivalents.
_UNICODE_MAP = {
    "\u2014": "-",   # em dash  →  hyphen
    "\u2013": "-",   # en dash  →  hyphen
    "\u2018": "'",   # left single curly quote
    "\u2019": "'",   # right single curly quote
    "\u201C": '"',   # left double curly quote
    "\u201D": '"',   # right double curly quote
    "\u2026": "...", # ellipsis
    "\u2022": "*",   # bullet
    "\u00A0": " ",   # non-breaking space
    "\u200B": "",    # zero-width space
    "\u2010": "-",   # hyphen
    "\u2011": "-",   # non-breaking hyphen
    "\u2012": "-",   # figure dash
    "\u2015": "-",   # horizontal bar
    "\u2212": "-",   # minus sign
    "\u00D7": "x",   # multiplication sign
}


def _sanitize(text: str) -> str:
    """Replace Unicode characters unsupported by Helvetica with safe equivalents."""
    for original, replacement in _UNICODE_MAP.items():
        text = text.replace(original, replacement)
    # Final safety net: replace any remaining non-Latin-1 chars
    return text.encode("latin-1", errors="replace").decode("latin-1")


class _ReportPDF(FPDF):
    """Custom FPDF subclass with branded header / footer."""

    def header(self):
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*_PRIMARY)
        self.cell(0, 12, "GodaamX", align="L")
        self.ln(6)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*_SECONDARY)
        self.cell(0, 6, "Inventory & Logistics ERP - Report", align="L")
        self.ln(10)
        # horizontal rule
        self.set_draw_color(*_ACCENT)
        self.set_line_width(0.6)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*_SECONDARY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


# ── Helpers ─────────────────────────────────────────────────────────

def _fmt(value: Any) -> str:
    """Format a value for display in the PDF."""
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:,.2f}"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return _sanitize(str(value))


def _pretty_key(key: str) -> str:
    """Convert a snake_case key to a Title Case label."""
    return key.replace("_", " ").title()


def _safe_cell(pdf: _ReportPDF, *args, **kwargs) -> None:
    """Wrapper that sanitizes text content before writing to a cell."""
    # Nothing to do here — we sanitize at the _fmt / data level
    pdf.cell(*args, **kwargs)


def _add_section_heading(pdf: _ReportPDF, title: str) -> None:
    """Render a section heading with a coloured background."""
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_fill_color(*_PRIMARY)
    pdf.set_text_color(*_WHITE)
    pdf.cell(0, 9, f"  {_sanitize(title)}", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)


def _add_cards_section(pdf: _ReportPDF, cards: dict[str, Any]) -> None:
    """Render key-value metric cards in a two-column grid."""
    _add_section_heading(pdf, "Key Metrics")
    pdf.set_font("Helvetica", "", 10)
    col_w = (pdf.w - 20) / 2
    items = list(cards.items())
    for idx in range(0, len(items), 2):
        for j in range(2):
            if idx + j >= len(items):
                break
            key, val = items[idx + j]
            x = 10 + j * col_w
            pdf.set_xy(x, pdf.get_y())
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*_SECONDARY)
            pdf.cell(col_w, 5, _sanitize(_pretty_key(key)), new_x="LMARGIN", new_y="NEXT" if j == 1 else "TOP")
            pdf.set_xy(x, pdf.get_y() + 5)
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(*_DARK_TEXT)
            pdf.cell(col_w, 7, _sanitize(_fmt(val)), new_x="LMARGIN", new_y="NEXT" if j == 1 else "TOP")
        pdf.ln(14)
    pdf.ln(2)


def _add_table(pdf: _ReportPDF, title: str, rows: list[dict[str, Any]]) -> None:
    """Render a list of dicts as a bordered table."""
    if not rows:
        return

    _add_section_heading(pdf, title)
    headers = list(rows[0].keys())
    n_cols = len(headers)
    col_w = (pdf.w - 20) / n_cols

    # Table header row
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(*_LIGHT_BG)
    pdf.set_text_color(*_PRIMARY)
    pdf.set_draw_color(*_BORDER)
    for h in headers:
        pdf.cell(col_w, 7, _sanitize(_pretty_key(h)), border=1, fill=True, align="C")
    pdf.ln()

    # Table data rows
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*_DARK_TEXT)
    fill = False
    for row in rows:
        # Check if we need a page break
        if pdf.get_y() + 7 > pdf.h - 20:
            pdf.add_page()
        if fill:
            pdf.set_fill_color(248, 250, 252)
        else:
            pdf.set_fill_color(*_WHITE)
        for h in headers:
            pdf.cell(col_w, 7, _sanitize(_fmt(row.get(h))), border=1, fill=True, align="C")
        pdf.ln()
        fill = not fill

    pdf.ln(6)


# ── Public API ──────────────────────────────────────────────────────

def build_dashboard_pdf(dashboard_data: dict[str, Any]) -> bytes:
    """
    Build a PDF report from dashboard JSON data.

    Parameters
    ----------
    dashboard_data : dict
        The JSON payload returned by the Dashboard API.

    Returns
    -------
    bytes
        The raw PDF bytes ready to be sent as a response.
    """
    pdf = _ReportPDF(orientation="L", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Generation timestamp ────────────────────────────────────────
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*_SECONDARY)
    pdf.cell(0, 6, f"Generated on: {now}", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Role badge ──────────────────────────────────────────────────
    role = dashboard_data.get("role", "N/A")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*_ACCENT)
    pdf.cell(0, 7, f"Dashboard Role: {_sanitize(str(role))}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Cards / KPIs ────────────────────────────────────────────────
    cards = dashboard_data.get("cards")
    if isinstance(cards, dict) and cards:
        _add_cards_section(pdf, cards)

    # ── Charts / Tables ─────────────────────────────────────────────
    charts = dashboard_data.get("charts")
    if isinstance(charts, dict):
        for chart_name, chart_data in charts.items():
            if isinstance(chart_data, list) and chart_data:
                _add_table(pdf, _pretty_key(chart_name), chart_data)

    # ── Catch-all: render any other top-level keys as tables ────────
    skip_keys = {"role", "cards", "charts"}
    for key, value in dashboard_data.items():
        if key in skip_keys:
            continue
        if isinstance(value, list) and value and isinstance(value[0], dict):
            _add_table(pdf, _pretty_key(key), value)
        elif isinstance(value, dict):
            _add_section_heading(pdf, _pretty_key(key))
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(*_DARK_TEXT)
            for k, v in value.items():
                pdf.cell(60, 7, _sanitize(_pretty_key(k)), new_x="RIGHT")
                pdf.cell(0, 7, _sanitize(_fmt(v)), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)

    # Output
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()
