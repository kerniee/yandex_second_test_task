import os

from decouple import config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app, get_db

if config("TEST_ON_SEPARATE_SQLITE", cast=bool, default=True):
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    DB_PATH = "test.db"

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    connect_args = {"check_same_thread": False}
else:
    if config('LOCAL', cast=bool, default=False):
        SQLALCHEMY_DATABASE_URL = str(config('DB_URL', default="sqlite:///./sql_app.db"))
    else:
        user = config("POSTGRES_USER")
        password = config("POSTGRES_PASSWORD")
        path = config("POSTGRES_DB")
        server = config("POSTGRES_TEST_SERVER")
        SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{server}/{path}"

    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    else:
        connect_args = {}
    connect_args["connect_timeout"] = 100

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
