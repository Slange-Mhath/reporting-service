from fastapi import HTTPException
import pytest
from main import app, check_for_api_token, empty_table, load_applications
from fastapi.testclient import TestClient
from applications.database import SessionLocal
from report.test_build_report import test_applications, session, engine

client = TestClient(app)
test_db = SessionLocal()


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Hey, this is the root endpoint. "
        "Don’t forget to set your "
        "'API_TOKEN' "
        "as env variable."
    }


def test_load_applications_fail(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "test_token")

    def mock_requests_get(url, headers, params):
        return type(
            "Response", (object,), {"status_code": 400, "text": "Bad Request"}
        )()

    monkeypatch.setattr("main.requests.get", mock_requests_get)
    response = client.post("/load_applications/")
    assert response.status_code == 400
    assert response.json() == {
        "detail": "There was a problem trying to access the API: Bad " "Request"
    }


def test_load_applications_key_error(monkeypatch):
    def mock_requests_get(url, headers, params):
        return type(
            "Response",
            (object,),
            {"status_code": 200, "json": lambda _: {"foobar": "barfoo"}},
        )()

    monkeypatch.setattr("main.requests.get", mock_requests_get)
    response = client.post("/load_applications/")
    assert response.status_code == 400
    assert response.json() == {
        "detail": "The response did not return the expected JSON."
    }


def test_report_on_db(test_applications):
    assert_report()


def test_report_on_empty_db(test_applications):
    """
    This is a bit of an all-round test, in a real-world scenario I’d hope to
     test all the functions and endpoints separately and isolated.
     However considering time constraints I will add that as a todo.
    """
    empty_table(test_db)
    assert_report()


def assert_report():
    response = client.get("/report/")
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["avg_processing_time"] == 291
    assert "annual_stat" in response_json
    assert "avg_processing_time" in response_json
    assert "long_waiting_application_ids" in response_json
    assert "status_per_research_area" in response_json


# def test_check_for_api_token(monkeypatch):
#     # Test case when API_TOKEN is not set
#     monkeypatch.delenv('API_TOKEN', raising=False)
#     response = client.post("/load_applications/")
#     assert response.status_code == 400
