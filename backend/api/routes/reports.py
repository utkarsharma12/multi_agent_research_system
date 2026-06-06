"""
Reports API routes — list, retrieve, and delete generated research reports.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Report
from database.schemas import ReportResponse, ReportListItem

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=list[ReportListItem])
def list_reports(db: Session = Depends(get_db)) -> list[ReportListItem]:
    """Return all reports (summary view) ordered by most recent."""
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return [ReportListItem.model_validate(r) for r in reports]


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)) -> ReportResponse:
    """Return the full content of a single report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return ReportResponse.model_validate(report)


@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)) -> dict:
    """Permanently delete a report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully."}
