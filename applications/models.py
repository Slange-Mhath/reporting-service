from enum import Enum

from sqlalchemy import Column, Integer, String, Date, Enum as EnumSA

from .database import Base


class Status(Enum):
    submitted = 1
    approved = 2
    rejected = 3


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String, unique=True, index=True)
    lead_applicant_name = Column(String)
    lead_applicant_email = Column(String)
    lead_applicant_address = Column(String)
    organisation_name = Column(String)
    summary = Column(String)
    amount_awarded = Column(Integer)
    research_area = Column(String)
    status = Column(EnumSA(Status), index=True)
    submitted_date = Column(Date, index=True)
    actioned_date = Column(Date, index=True)
