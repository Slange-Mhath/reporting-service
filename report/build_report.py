import calendar
from typing import List
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from applications.models import Application, Status
from sqlalchemy import and_, func, or_
from datetime import datetime, timedelta


def build_report(db: Session) -> dict:
    """Build it all together and create the final report."""
    report = {
        "status_per_research_area": get_application_status_per_research_area(db),
        "annual_stat": create_annual_stat(db),
        "avg_processing_time": get_avg_time_between_submitted_and_actioned(db),
        "long_waiting_application_ids": get_long_waiting_applications(db),
    }
    return report


def get_application_status_per_research_area(db: Session) -> dict:
    """Get the applications status per research area.

    :param db: The database session
    :return: A dictionary with the research area as key and a dictionary
    This filters out the application_ids which have been submitted, approved or
    rejected by research_area. It uses the count function to count the total
    number and groups them by research_area. It returns a list of sql alchemy
    rows like ('infectious_disease', 0, 1, 0) and builds the dict from there.
    The task it not 100% clear if it should return the total number of
    applications which got submitted or which have the status submitted.
    As the task is saying submitted and every approved and rejected application
    was submitted we can safely assume that all applications with a
    submitted_date should get counted.
    """
    results = (
        db.query(
            Application.research_area,
            func.count(Application.id)
            .filter(Application.submitted_date.isnot(None))
            .label("submitted"),
            func.count(Application.id)
            .filter(Application.status == Status.approved)
            .label("approved"),
            func.count(Application.id)
            .filter(Application.status == Status.rejected)
            .label("rejected"),
        )
        .group_by(Application.research_area)
        .all()
    )

    research_areas = {}
    for result in results:
        research_areas[result.research_area] = {
            "submitted": result.submitted,
            "approved": result.approved,
            "rejected": result.rejected,
        }
    return research_areas


def create_annual_stat(db: Session) -> dict:
    """
    Create the annual statistic with the last 12 months.

    :param db: The database session
    :return: A dictionary with the year as key and a dictionary with the months
    It iterates over the last 12 months and using i month for the key of the
    created annual statistic dictionary. This then gets enriched by the keys
    submitted, approved and rejected which call functions to get the number
    of the respective applications. It also adds an approved_funding key which
    calls a function to calculate the approved funding of a given month. This
    function could get optimised to use less SQL queries and filter on a
    bigger queryset to improve performance. It also assumes  that rejections
    have no actioned_date and therefore counts the rejection to the month
    of the submission date. This seems a bit odd to me but the data in the
    api seems to not have a single application which is rejected and has
    an actioned_date. So I guess its save to assume that it got rejected
    on submission which is why the rejection is counted for the month of
    the submission. Also, worth noting that, submitted is not filtering on
    any status but assumes that every application, rejected or approved
    was submitted and therefore should be counted  for the month of
    submitting_date.
    """
    annual_stat = {}
    for i in range(12):
        month = datetime.today() - relativedelta(months=i)
        year = month.year
        month_num = month.strftime("%m")
        annual_stat.setdefault(year, {})[month_num] = {
            "submitted": get_num_of_appl_given_status_month(db, month),
            "approved": get_num_of_appl_given_status_month(db, month, Status.approved),
            "rejected": get_num_of_appl_given_status_month(db, month, Status.rejected),
            "approved_funding": get_approved_funding_given_month(db, month),
        }
    return annual_stat


def get_num_of_appl_given_status_month(
    db: Session, month_date: datetime, status: Status = None
) -> int:
    """Returns all applications in a given month wit a given status.

    :param db: The database session
    :param month_date: The datetime of the month of the applications
    :param status: The status of the applications
    :return: The number of applications in a given month with a given status
    """
    start_date, end_date = get_month_date_range(month_date)
    all_submissions = db.query(func.count(Application.id)).filter(
        and_(
            Application.submitted_date >= start_date,
            Application.submitted_date <= end_date,
        )
    )
    if status == Status.rejected:
        # Assuming that rejected applications have no actioned_date and are
        # rejected on submission, which I would want to ask!
        return all_submissions.filter(Application.status == status).scalar()
    elif status == Status.approved:
        return (
            db.query(func.count(Application.id))
            .filter(
                and_(
                    Application.status == status,
                    Application.actioned_date >= start_date,
                    Application.actioned_date <= end_date,
                )
            )
            .scalar()
        )
    else:
        return all_submissions.scalar()


def get_month_date_range(month_date: datetime) -> tuple:
    """Returns the start and end date of a given month."""
    num_days_in_month = calendar.monthrange(month_date.year, month_date.month)[1]
    start_date = month_date.replace(day=1)
    end_date = month_date.replace(day=num_days_in_month)
    return start_date.date(), end_date.date()


def get_approved_funding_given_month(db: Session, month_date: datetime) -> float:
    """Returns the approved funding of a given month.

    :param db: The database session
    :param month_date: The datetime of the month of the applications
    :return: The approved funding of a given month
    """
    start_date, end_date = get_month_date_range(month_date)
    return (
        db.query(func.sum(Application.amount_awarded))
        .filter(
            and_(
                Application.actioned_date >= start_date,
                Application.actioned_date <= end_date,
                Application.status == Status.approved,
            )
        )
        .scalar()
    )


def get_avg_time_between_submitted_and_actioned(db: Session) -> int:
    """Returns the average time between submitted and actioned in days.

    :param db: The database session
    :return: The average time between submitted and actioned in days
    Calculates the time between action date and
    submitted date, to then use the avg function to get the average, which
    basically divides through the filtered application count. Finally, the
    minutes get converted into days and rounded appropriately to only return
    full days.
    """
    avg_minutes_to_actioned = (
        db.query(
            func.avg(
                (
                    func.strftime("%s", Application.actioned_date)
                    - func.strftime("%s", Application.submitted_date)
                )
                / 60
            )
        )
        .filter(
            and_(
                Application.submitted_date.isnot(None),
                Application.actioned_date.isnot(None),
                or_(
                    Application.status == Status.approved,
                    Application.status == Status.rejected,
                ),
            ),
        )
        .scalar()
    )
    return round(avg_minutes_to_actioned / 1440)


def get_long_waiting_applications(db: Session) -> List[str]:
    """Get application ids which have not been actioned in more than 60 days.

    :param db: The database session
    :return: A list of application ids which have not been actioned in 60 days
    this function first defines a cutoff_date which is 60 days from the
    current date in the past. It then filters through all applications which
    have the status submitted and the submitted date is before the cutoff
    date. To ensure that the ids are returned as a List of String the
    function iterates over the row of returned ids and appends them in a
    list which is getting returned.
    """
    cutoff_date = datetime.now() - timedelta(days=60)

    long_waiting_applications = (
        db.query(Application.application_id)
        .filter(
            and_(
                Application.status == Status.submitted,
                Application.submitted_date <= cutoff_date,
            )
        )
        .all()
    )
    application_ids = []
    for appl in long_waiting_applications:
        application_ids.append(appl.application_id)
    return application_ids
