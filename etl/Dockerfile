FROM python:3.11-slim

WORKDIR /app

RUN pip install wbgapi pandas sqlalchemy psycopg2-binary

COPY etl.py .
COPY oecd_hours_transformed.csv .

CMD ["python", "etl.py"]
