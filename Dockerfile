FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir app
RUN cd /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .env .
COPY source .