import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from applications import models
from applications.database import engine, SessionLocal, Base
import requests
from report.build_report import build_report
from applications.crd import create_application
from report.schemas import Report

info_logger = logging.getLogger("uvicorn.info")
error_logger = logging.getLogger("uvicorn.error")

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    """This is the root endpoint.

    It is used to check if the API is running.
    """
    return {
        "message": "Hey, this is the root endpoint. "
        "Don’t forget to set your "
        "'API_TOKEN' "
        "as env variable."
    }


def get_db():
    """Dependency to get the database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_for_api_token():
    """Check if the API_TOKEN is set as an environment variable."""
    info_logger.info("Checking for API_TOKEN ...")
    if os.environ.get("API_TOKEN") is None:
        error_logger.error("API_TOKEN is not set in the environment")
        raise HTTPException(
            status_code=400,
            detail="Ooops, that did not work. Make sure you "
            "have the right API TOKEN set in the "
            "environment. To double check revisit the "
            "documentation.",
        )


def get_data_from_api(skip: int, limit: int) -> dict:
    """This returns the data from the API.

    :param skip: The number of records to skip
    :param limit: The number of records to return
    :return: The json response from the API
    With the skip and limit parameters we can paginate through the API.
    """
    headers = get_api_header(API_TOKEN)
    info_logger.info(f"Getting data from the API with skip={skip} and limit={limit}")
    response = requests.get(
        API_URL, headers=headers, params={"limit": limit, "skip": skip}
    )
    if response.status_code != 200:
        error_logger.error(f"API returned status code {response.status_code}")
        raise HTTPException(
            status_code=response.status_code,
            detail=f"There was a problem trying to access the API:" f" {response.text}",
        )
    return response.json()


@app.post("/load_applications/")
async def load_applications(db: Session = Depends(get_db)):
    """This endpoint loads the applications from the API into the DB.

    :param db: The database session
    :return: A message with the number of applications loaded into the DB
    This function simulats a do while loop, which does not exist in Python.
    It comes in handy here, to ensure that we get the total number of records
    first so that we can ensure that all records are loaded into the DB. This
    is done by checking if the skip parameter is greater than the total number
    of records. If it is, we break out of the loop. If not, we continue to
    load the data from the API into the DB and save bulk save it into the DB.
    """
    check_for_api_token()
    empty_table(db)
    skip = 0
    limit = 50000
    applications = []
    count = 0
    try:
        while True:
            response_json = get_data_from_api(skip, limit)
            total_number_of_records = response_json["available_records"]
            if skip > total_number_of_records:
                break
            for item in response_json["items"]:
                db_application = create_application(item)
                applications.append(db_application)
                count += 1
                if count % 1000 == 0:
                    percentage_complete = count / total_number_of_records * 100
                    info_logger.info(
                        f"Processing: {int(percentage_complete)}% loaded..."
                    )
            skip += limit
    except KeyError:
        error_logger.error(f"The response did not return the expected JSON format.")
        raise HTTPException(
            status_code=400, detail="The response did not " "return the expected JSON."
        )
    db.bulk_save_objects(applications)
    db.commit()
    info_logger.info(f"{count} Applications loaded into database")
    return {"message": f"{count} applications successfully loaded into database."}


@app.get("/report/", response_model=Report)
async def report(db: Session = Depends(get_db)):
    """This endpoint builds the report.

    :param db: The database session
    :return: The report
    This function checks if the DB is empty. If it is, it calls the function
    to load the data from the API into the DB and waits for it to finish. If
    it is not empty, it builds the report, according to the given schema.
    """
    if db.query(models.Application).count() == 0:
        error_logger.warning(
            "Seems like we need to get the data from the API"
            " before the report can be built. This might take"
            " a couple of minutes..."
        )
        await load_applications(db)
    info_logger.info("Building report...")
    return build_report(db)


API_URL = "https://example-api.org/api"
API_TOKEN = os.environ.get("API_TOKEN")


def empty_table(db: Session):
    """Creates a clean slate for the database."""
    info_logger.info("Clearing database...")
    db.query(models.Application).delete()
    db.commit()


def get_api_header(api_token: str) -> dict:
    """Provides the header for the API request."""
    headers = {"Authorization": "Bearer {token}".format(token=api_token)}
    return headers
