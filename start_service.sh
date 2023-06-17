#!/bin/bash
set -m

ENDPOINT="/load_applications/"

uvicorn main:app --reload --host 0.0.0.0 &
sleep 5
curl -X POST http://localhost:8000${ENDPOINT}
fg