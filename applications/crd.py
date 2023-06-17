from datetime import datetime
from fastapi import HTTPException
from .models import Application
from .schemas import ApplicationBase
import logging

error_logger = logging.getLogger("uvicorn.error")


def to_datetime_obj(date_str: str) -> datetime or None:
    """Convert string to datetime to fit the database schema."""
    if date_str:
        try:
            actioned_date = datetime.strptime(date_str, "%Y-%m-%d")
            return actioned_date
        except ValueError:
            error_logger.error("Incorrect data format, should be YYYY-MM-DD")
            return None


def create_application(item: dict) -> Application:
    """Create an application object from the API response item.

    :param item: The item from the API response
    :return: The application object according to schema
    """
    try:
        application = ApplicationBase(**item)
    except Exception as e:
        error_logger.error(f"Invalid data: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    submitted_date = application.submitted_date
    actioned_date = application.actioned_date
    db_application = Application(
        application_id=application.application_id,
        lead_applicant_name=application.lead_applicant_name,
        lead_applicant_email=application.lead_applicant_email,
        lead_applicant_address=application.lead_applicant_address,
        organisation_name=application.organisation_name,
        summary=application.summary,
        amount_awarded=application.amount_awarded,
        research_area=application.research_area,
        status=application.status,
        submitted_date=submitted_date,
        actioned_date=actioned_date,
    )
    return db_application
