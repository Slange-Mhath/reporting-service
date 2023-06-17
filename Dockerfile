FROM python:3.10
WORKDIR /code-example
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .

CMD ./start_service.sh
