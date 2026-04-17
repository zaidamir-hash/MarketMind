from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import ScraperLog
from app.etl.etl_utils import utc_now


def create_scraper_log_start(db: Session, job_name: str) -> ScraperLog:
    log = ScraperLog(
        job_name=job_name,
        status="FAIL",
        started_at=utc_now(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def finish_scraper_log_success(db: Session, log: ScraperLog, rows_inserted: int) -> ScraperLog:
    log.status = "SUCCESS"
    log.rows_inserted = rows_inserted
    log.error_message = None
    log.finished_at = utc_now()
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def finish_scraper_log_fail(db: Session, log: ScraperLog, error_message: str) -> ScraperLog:
    log.status = "FAIL"
    log.error_message = error_message[:5000]
    log.finished_at = utc_now()
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
