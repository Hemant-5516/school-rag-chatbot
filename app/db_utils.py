import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

MYSQL_URI = os.getenv("MYSQL_URI")

engine = create_engine(MYSQL_URI)

def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES;"))
            tables = [row[0] for row in result]
        return True, tables
    except SQLAlchemyError as e:
        return False, str(e) 