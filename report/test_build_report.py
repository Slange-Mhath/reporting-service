from datetime import date, datetime, timedelta
from pprint import pprint
import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from applications.models import Base, Application, Status
from .build_report import (
    build_report,
    create_annual_stat,
    get_application_status_per_research_area,
    get_approved_funding_given_month,
    get_avg_time_between_submitted_and_actioned,
    get_long_waiting_applications,
    get_month_date_range,
    get_num_of_appl_given_status_month,
)


@pytest.fixture(scope="session")
def engine():
    # use an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def my_datetime():
    return datetime(2023, 1, 1, 13, 18, 11, 558836)


@pytest.fixture
def my_feb_datetime():
    return datetime(2023, 2, 15, 13, 18, 11, 558836)


@pytest.fixture
def test_applications(session):
    applications = [
        Application(
            application_id="4f5f4397-fe57-4a5d-a968-960b9def4452",
            lead_applicant_name="Alice",
            lead_applicant_email="alice@example.com",
            lead_applicant_address="123 Main St",
            organisation_name="OrgA",
            summary="A research proposal",
            amount_awarded=1000,
            research_area="mental_health",
            status="submitted",
            submitted_date=date(2023, 1, 1),
            actioned_date=None,
        ),
        Application(
            application_id="37aaa73e-1ae8-4edb-9dfc-aa1d403d6c25",
            lead_applicant_name="Alice",
            lead_applicant_email="alice@example.com",
            lead_applicant_address="123 Main St",
            organisation_name="OrgA",
            summary="A research proposal",
            amount_awarded=1000,
            research_area="mental_health",
            status="approved",
            submitted_date=date(2023, 1, 1),
            actioned_date=date(2023, 3, 2),
        ),
        Application(
            application_id="2be2f277-fca3-4fba-8d48-c3bf48098a4b",
            lead_applicant_name="Alice",
            lead_applicant_email="alice@example.com",
            lead_applicant_address="123 Main St",
            organisation_name="OrgA",
            summary="A research proposal",
            amount_awarded=1000,
            research_area="mental_health",
            status="submitted",
            submitted_date=date(2023, 1, 25),
            actioned_date=None,
        ),
        Application(
            application_id="190476b9-8244-4e5f-bc9a-6688f88baf79",
            lead_applicant_name="Alice",
            lead_applicant_email="alice@example.com",
            lead_applicant_address="123 Main St",
            organisation_name="OrgA",
            summary="A research proposal",
            amount_awarded=1000,
            research_area="mental_health",
            status="submitted",
            submitted_date=date(2023, 4, 1),
            actioned_date=None,
        ),
        Application(
            application_id="3b13a2a5-0d0b-4c92-b7b4-02b30d3fd677",
            lead_applicant_name="Alice",
            lead_applicant_email="alice@example.com",
            lead_applicant_address="123 Main St",
            organisation_name="OrgA",
            summary="A research proposal",
            amount_awarded=1000,
            research_area="mental_health",
            status="submitted",
            submitted_date=date(2022, 1, 3),
            actioned_date=None,
        ),
        Application(
            application_id="323ad928-9edd-4ae6-9e8c-9ecb1819e12a",
            lead_applicant_name="Alice",
            lead_applicant_email="alice@example.com",
            lead_applicant_address="123 Main St",
            organisation_name="OrgA",
            summary="A research proposal",
            amount_awarded=1000,
            research_area="mental_health",
            status="approved",
            submitted_date=date(2023, 6, 4),
            actioned_date=date(2023, 11, 5),
        ),
        Application(
            application_id="f62436b4-7bf2-42c5-9060-63a07abf6ee0",
            lead_applicant_name="Bob",
            lead_applicant_email="bob@example.com",
            lead_applicant_address="456 Elm St",
            organisation_name="OrgB",
            summary="Another research proposal",
            amount_awarded=2000,
            research_area="infectious_disease",
            status="approved",
            submitted_date=date(2023, 1, 6),
            actioned_date=date(2023, 1, 7),
        ),
        Application(
            application_id="fe67ba73-7aec-4d3f-a6dc-1e8c27c097ae",
            lead_applicant_name="Charlie",
            lead_applicant_email="charlie@example.com",
            lead_applicant_address="789 Oak St",
            organisation_name="OrgC",
            summary="Yet another research proposal",
            amount_awarded=3000,
            research_area="climate_and_health",
            status="rejected",
            submitted_date=date(2023, 1, 8),
            actioned_date=None,
        ),
        Application(
            application_id="e01c7b9e-e0f3-4672-9e16-7a67f78f1b59",
            lead_applicant_name="Charlie",
            lead_applicant_email="charlie@example.com",
            lead_applicant_address="789 Oak St",
            organisation_name="OrgC",
            summary="Yet another research proposal",
            amount_awarded=3000,
            research_area="climate_and_health",
            status="rejected",
            submitted_date=date(2023, 1, 8),
            actioned_date=None,
        ),
        Application(
            application_id="8a9414b1-4b35-4ad4-94db-89b4aac365ff",
            lead_applicant_name="Charlie",
            lead_applicant_email="charlie@example.com",
            lead_applicant_address="789 Oak St",
            organisation_name="OrgC",
            summary="Yet another research proposal",
            amount_awarded=3000,
            research_area="climate_and_health",
            status="rejected",
            submitted_date=date(2023, 1, 8),
            actioned_date=date(2023, 1, 9),
        ),
    ]
    session.add_all(applications)
    session.commit()
    return applications


def test_get_application_status_per_research_area(session, test_applications):
    research_area_report = get_application_status_per_research_area(session)
    expected = {
        "mental_health": {"submitted": 6, "approved": 2, "rejected": 0},
        "infectious_disease": {"submitted": 1, "approved": 1, "rejected": 0},
        "climate_and_health": {"submitted": 3, "approved": 0, "rejected": 3},
    }
    assert research_area_report == expected


def test_get_long_waiting_applications(session, test_applications):
    long_waiting_application_ids = get_long_waiting_applications(session)
    cutoff_date = datetime.now() - timedelta(days=60)
    for appl in long_waiting_application_ids:
        application = session.query(Application).filter_by(application_id=appl).first()
        assert application.status == Status.submitted
        assert application.submitted_date <= cutoff_date.date()
    assert len(long_waiting_application_ids) == 3


def test_create_annual_stat(session, test_applications):
    annual_stat = create_annual_stat(session)
    for i in range(12):
        month = datetime.today() - relativedelta(months=i)
        year = month.year
        month_num = month.strftime("%m")
        assert year in annual_stat
        assert month_num in annual_stat[year]


def test_get_monthly_applications_with_given_status(
    session, test_applications, my_datetime
):
    rejected_count = get_num_of_appl_given_status_month(
        session, my_datetime, Status.rejected
    )
    submitted_count = get_num_of_appl_given_status_month(
        session,
        my_datetime,
    )
    approved_count = get_num_of_appl_given_status_month(
        session, my_datetime, Status.approved
    )

    assert approved_count == 1
    assert submitted_count == 7
    assert rejected_count == 3


def test_get_approved_funding_given_month(session, test_applications, my_datetime):
    approved_funding = get_approved_funding_given_month(session, my_datetime)
    assert approved_funding == 2000


def test_get_avg_time_between_submitted_and_actioned(session, test_applications):
    avg_time = get_avg_time_between_submitted_and_actioned(session)
    actioned_applications = (
        session.query(Application).filter(Application.actioned_date.isnot(None)).all()
    )
    processing_time = 0
    for appl in actioned_applications:
        days_between = (appl.actioned_date - appl.submitted_date).days
        processing_time += days_between
    avg_time_days = processing_time / len(actioned_applications)
    assert avg_time == avg_time_days


def test_build_report(session, test_applications):
    report = build_report(session)
    keys_in_report = [
        "annual_stat",
        "status_per_research_area",
        "avg_processing_time",
        "long_waiting_application_ids",
    ]
    for key in keys_in_report:
        assert key in report.keys()
        assert report[key] is not None


def test_get_month_date_range(my_datetime, my_feb_datetime):
    start_date, end_date = get_month_date_range(my_datetime)
    assert start_date == date(2023, 1, 1)
    assert end_date == date(2023, 1, 31)
    start_date, end_date = get_month_date_range(my_feb_datetime)
    assert start_date == date(2023, 2, 1)
    assert end_date == date(2023, 2, 28)
