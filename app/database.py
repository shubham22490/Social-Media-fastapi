from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings

SQLALCHEMY_DB_URL = f'postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}:{settings.db_port}/{settings.db_name}'

engine = create_engine(SQLALCHEMY_DB_URL, echo=True)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()

# Initialsing wit the db driveer to send raw queries.
# while True:
#     try:
#         conn = psycopg2.connect(host='172.21.160.1',  database='fastapi', user='postgres', password='', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection Succesful!")
#         break
#     except Exception as err:
#         print(f"Connection failed with error: {err}")
#         time.sleep(2)


# my_posts = [{"title": "post1", "content": "post1 content.", "id": 1}]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()