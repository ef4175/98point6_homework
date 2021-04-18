FROM python:3.9.4

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY payload_schema.py .
COPY game_objects.py .
COPY helpers.py .
COPY exceptions.py .
COPY unit_tests unit_tests
COPY functional_tests functional_tests
