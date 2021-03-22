FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

RUN mkdir app
RUN cd /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apt-get update
RUN apt-get install postgresql-client postgresql-client-common python-psycopg2 -y

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY source/prestart.sh .
RUN ["chmod", "+x", "prestart.sh"]

COPY source .
