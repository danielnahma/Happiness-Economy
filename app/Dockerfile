FROM python:3.11-slim

WORKDIR /app

RUN pip install streamlit pandas numpy plotly sqlalchemy psycopg2-binary statsmodels

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
