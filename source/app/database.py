from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if config('LOCAL', cast=bool):
    SQLALCHEMY_DATABASE_URL = str(config('DB_URL', default="sqlite:///./sql_app.db"))
else:
    user = config("POSTGRES_USER")
    password = config("POSTGRES_PASSWORD")
    path = config("POSTGRESS_DB")
    server = config("POSTGRESS_SERVER")
    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{server}/{path}"

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    check_same_thread = False
else:
    check_same_thread = True

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": check_same_thread}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
