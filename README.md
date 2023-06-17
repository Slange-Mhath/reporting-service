<!-- ABOUT THE PROJECT -->

## Report-Service API

![FastAPI][FastAPI-img] ![SQLite][SQLite-img] ![Python][Python-img] ![macOs]
![Linux] ![Docker] ![Swagger-UI][Swagger]

![Pytest] ![Black]

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about">About</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#dependencies">Dependencies</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#using-docker">Installation with Docker</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
        <ul>
        <li><a href="#quick-start-via-bash-script">Quick Start</a></li>
        <li><a href="#manual-start">Manual Start</a></li>
        <li><a href="#endpoints">Endpoints</a></li>
        </ul>
  </ol>
</details>


<!-- About-->

## About

This small web application helps collecting and analysing data about
applications for funding to identify trends and patterns.

**This is a dummy project and not intended to be used in production. It
exclusively serves the purpose to develop my FastAPI and Python skills further**

The system providing the data via an API accepts form submissions from our
grants system, each application has a set of fields which describe the research
the application is intended for.

- Written in Python3+
- Accepts a GET request over HTTP
- Does not require authentication (it will be deployed internally)
- Returns a JSON (i.e. application/json) response containing a sumulative report
  about the grant applications
- The report that the service returns should contain the following information

- The total number of submitted, approved and rejected applications per research
  area
- For each of the past 12 months, the total submitted, approved, and rejected
  applications in each month
- For each of the past 12 months, the sum of funding we approved in each month
  based on the applications data.
- The average time in (days) between an application being received (submitted)
  and an outcome (approved or rejected)
- A list of application ids which have not been actioned in more than 60 days
  from their submitted date (i.e. they are still in the submitted state).

<!-- GETTING STARTED -->

## Getting Started

<!-- Dependencies -->

### Dependencies

**This code is developed and tested to be deployed on macOS or Linux. It is
not tested on Windows. I recommend using the <a href="#using-docker">
Installation with Docker</a> for Windows users.**

- Python Version 3.10
- SQLAlchemy Version 2.0.8
- FastAPI 0.95.0
- Python-dateutil 2.8.2

To install all dependencies navigate into the project folder and run:

   ```sh
   pip install -r requirements.txt
   ```

<!-- Installation -->

### Installation

1. Clone the repo
   ```sh
   git clone git@github.com:Slange-Mhath/reporting-service.git
   ```

2. Navigate into the project directory
   ```sh
   cd reporting-service
   ```

3. Set the API_TOKEN as environment variable
   ```sh
   export API_TOKEN=your_api_token
   ```

4. Run uvicorn to start the server
   ```sh
   uvicorn main:app --reload
   ```

### Using Docker

If you want to run this service in a Docker Container, no problem at all!

1. Clone the repo
   ```sh
   git clone git@github.com:Slange-Mhath/reporting-service.git

2. Navigate into the project directory
   ```sh
   cd reporting-service
   ```
3. Build the Docker image
   ```sh
    docker build -t reporting-service .
    ```
4. Run the Docker container providing the **API_TOKEN** as environment
   variable and
   ```sh
   docker run -e API_TOKEN=YOUR-API-TOKEN -d --name my-reporting-service -p 
   8000:8000 reporting-service
   ```
5. After a couple of minutes you should be able to access your container at
   http://127.0.0.1:8000/

<!-- USAGE -->

## Usage

### Quick Start via Bash Script

To start up the server and get ready to request the report simply run:

```sh
./start_service.sh
```

This might take a couple of minutes if you run the command for the first time,
as the DB needs to be filled by the requested data.
You will then see the message:

_"110000 applications successfully loaded into database."_

Now you can access the endpoint in your browser http://127.0.0.1:8000/report/

### Manual Start

You can of course also start the server and load the data manually by running
the following commands:

```sh
uvicorn main:app --reload
```

and accessing:

### Endpoints

**[GET] http://127.0.0.1:8000/report/**

**Again, be aware that, if you access the endpoint for the first time, it might
take a couple of minutes until you get a response.**

If you want to update the data (e.g. when the data provided by the application
changes) you can access the endpoint:

**[POST] http://127.0.0.1:8000/load_applications/**

If you are curious about the available endpoints have a look at the:

**Swagger UI http://127.0.0.1:8000/docs**

or

**ReDoc UI at http://127.0.0.1:8000/redoc**


[FastAPI-img]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi

[Python-img]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54

[macOS]: https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=macos&logoColor=F0F0F0

[Linux]: https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black

[Docker]:https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white

[Swagger]: https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white

[Black]: https://img.shields.io/badge/code%20style-black-000000.svg

[Pytest]: https://img.shields.io/badge/Pytest-passing-sucess

[SQLite-img]: https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white

[FastAPI]: https://fastapi.tiangolo.com/

[Swagger-UI]: https://github.com/swagger-api/swagger-ui


