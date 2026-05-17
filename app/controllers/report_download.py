"""
Controller for the Report Download API.

Fetches data from a Dashboard API endpoint, transforms it into a
formatted PDF report, and returns the PDF bytes.
"""

from __future__ import annotations

import httpx
from fastapi import HTTPException

from app.utils.pdf_builder import build_dashboard_pdf


async def generate_report_pdf(dashboard_url: str) -> bytes:
    """
    Fetch dashboard data from *dashboard_url*, convert it to a PDF.

    Parameters
    ----------
    dashboard_url : str
        Fully qualified URL pointing to a Dashboard API JSON endpoint.

    Returns
    -------
    bytes
        Raw PDF content.

    Raises
    ------
    HTTPException
        On network errors, non-200 responses or invalid JSON.
    """
    # ── 1. Fetch dashboard data ─────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(dashboard_url)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reach the Dashboard API: {exc}",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Dashboard API returned status {resp.status_code}: "
                f"{resp.text[:300]}"
            ),
        )

    try:
        data = resp.json()
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Dashboard API did not return valid JSON.",
        )

    # ── 2. Build PDF ────────────────────────────────────────────────
    try:
        pdf_bytes = build_dashboard_pdf(data)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {exc}",
        )

    return pdf_bytes
