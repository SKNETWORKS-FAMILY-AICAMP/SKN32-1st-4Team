import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


# MySQL 데이터베이스 연결 엔진을 생성하는 함수이다.
# 다른 파일에서 get_engine()을 호출하면 MySQL에 연결할 수 있는 객체를 받을 수 있다.
def get_engine():
    # .env 파일에서 값을 읽는다.
    host = os.getenv("DB_HOST", "")
    port = os.getenv("DB_PORT", "")
    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "")

    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"

    return create_engine(db_url, pool_pre_ping=True)
