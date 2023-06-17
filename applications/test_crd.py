from datetime import datetime
import pytest
from .models import Application

from .crd import to_datetime_obj, create_application


@pytest.fixture
def valid_date_str():
    return "2020-11-02"


@pytest.fixture
def invalid_date_str():
    return "2020/11/20"


@pytest.fixture
def test_record():
    item1 = {
        "application_id": "55128",
        "lead_applicant_name": "John Doe",
        "lead_applicant_email": "johndoe@example.com",
        "lead_applicant_address": "Geschwister-Scholl-Str. 2",
        "organisation_name": "ADW Mainz",
        "summary": "Lorem ipsum",
        "amount_awarded": 5000,
        "research_area": "Science",
        "status": "approved",
        "submitted_date": "2022-01-01",
        "actioned_date": "2022-01-05",
    }
    return item1


@pytest.fixture
def invalid_test_record():
    item1 = {
        "application_id": "",
        "lead_applicant_name": "John Doe",
        "lead_applicant_email": "johndoe@example.com",
        "lead_applicant_address": "Geschwister-Scholl-Str. 2",
        "organisation_name": "ADW Mainz",
        "summary": "Lorem ipsum",
        "amount_awarded": 5000,
        "research_area": "assds",
        "status": "approved",
        "submitted_date": "2022-01-01",
        "actioned_date": "2022-01-05",
    }
    return item1


def test_to_datetime_obj_with_valid_date(valid_date_str):
    assert to_datetime_obj(valid_date_str) == datetime(2020, 11, 2)


def test_to_datetime_obj_with_invalid_date(invalid_date_str):
    assert to_datetime_obj(invalid_date_str) is None


def test_to_datetime_obj_with_empty_string():
    assert to_datetime_obj("") is None


def test_check_eq_of_values_in_isolation_of_datetime(test_record):
    expected_item = {
        "application_id": "55128",
        "lead_applicant_name": "John Doe",
        "lead_applicant_email": "johndoe@example.com",
        "lead_applicant_address": "Geschwister-Scholl-Str. 2",
        "organisation_name": "ADW Mainz",
        "summary": "Lorem ipsum",
        "amount_awarded": 5000,
        "research_area": "Science",
        "status": "approved",
        "submitted_date": datetime.strptime("2022-01-01", "%Y-%m-%d").date(),
        "actioned_date": datetime.strptime("2022-01-05", "%Y-%m-%d").date(),
    }
    created_application = create_application(test_record)
    # Iterate over the first 9 keys to avoid comparing datetime, which gets
    # tested in a separate test so that we can test the functions in isolation.
    # This is a bit of a hack, but it works.
    for key, value in list(expected_item.items())[:9]:
        assert getattr(created_application, key) == value


def test_correct_class_type_created(test_record):
    created_application = create_application(test_record)
    assert isinstance(created_application, Application)
