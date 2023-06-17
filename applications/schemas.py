from typing import Optional

from pydantic import BaseModel
from datetime import date


class ApplicationBase(BaseModel):
    application_id: str
    lead_applicant_name: Optional[str] = None
    lead_applicant_email: Optional[str] = None
    lead_applicant_address: Optional[str] = None
    organisation_name: Optional[str] = None
    summary: Optional[str] = None
    amount_awarded: int
    research_area: str
    status: str
    submitted_date: date
    actioned_date: Optional[date] = None
