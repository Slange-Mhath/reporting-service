from typing import Dict, List, Optional
from pydantic import BaseModel, validator


class MonthStatWithoutFunding(BaseModel):
    submitted: int
    approved: int
    rejected: int


class MonthStat(MonthStatWithoutFunding):
    approved_funding: Optional[float] = None


class YearStat(BaseModel):
    __root__: Dict[int, MonthStat]


class AnnualStat(BaseModel):
    __root__: Dict[int, YearStat]


class StatusPerResearchArea(BaseModel):
    infectious_disease: MonthStatWithoutFunding
    mental_health: MonthStatWithoutFunding
    climate_and_health: MonthStatWithoutFunding


class Report(BaseModel):
    annual_stat: AnnualStat
    avg_processing_time: float
    long_waiting_application_ids: List[str]
    status_per_research_area: StatusPerResearchArea
