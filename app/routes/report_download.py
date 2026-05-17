"""
Route for downloading a Dashboard report as a PDF.

GET /api/v1/report/download?dashboardUrl=<url>
"""

from typing import Annotated

import asyncpg
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response

from app.controllers import report_download as report_download_ctrl
from app.database import get_connection
from app.utils.dependencies import get_current_user

router = APIRouter()

Conn = Annotated[asyncpg.Connection, Depends(get_connection)]
CurrentUser = Annotated[dict, Depends(get_current_user)]


@router.get("/download")
async def download_report(
    request: Request,
    current_user: CurrentUser,
    dashboardUrl: str = Query(
        default=None,
        description=(
            "Fully-qualified URL of the Dashboard API to fetch data from. "
            "If omitted, the internal dashboard endpoint is used."
        ),
    ),
):
    """
    Fetch data from the given Dashboard API, generate a PDF report,
    and return it as a downloadable file.

    - **dashboardUrl**: (optional) external Dashboard API URL.
      When not provided the server calls its own ``/api/v1/dashboard/``
      endpoint, forwarding the caller's auth token.
    """
    # ── Resolve the dashboard URL ───────────────────────────────────
    if not dashboardUrl:
        # Build the internal dashboard URL from the incoming request
        base = str(request.base_url).rstrip("/")
        dashboardUrl = f"{base}/api/v1/dashboard/"

        # Forward the caller's Bearer token so the internal call is
        # authenticated with the same credentials.
        auth_header = request.headers.get("authorization", "")
        if auth_header:
            dashboardUrl_with_auth = dashboardUrl  # URL stays the same
        else:
            dashboardUrl_with_auth = dashboardUrl
    else:
        auth_header = ""
        dashboardUrl_with_auth = dashboardUrl

    # ── Fetch + generate ────────────────────────────────────────────
    import httpx
    from fastapi import HTTPException
    from app.utils.pdf_builder import build_dashboard_pdf

    try:
        headers = {}
        if auth_header:
            headers["Authorization"] = auth_header

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(dashboardUrl, headers=headers)
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

    try:
        pdf_bytes = build_dashboard_pdf(data)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {exc}",
        )

    # ── Return as downloadable PDF ──────────────────────────────────
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="report.pdf"',
        },
    )
