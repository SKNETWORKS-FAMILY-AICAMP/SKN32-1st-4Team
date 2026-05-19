import pandas as pd
from sqlalchemy import create_engine

def get_db_engine():
    db_url = "mysql+mysqlconnector://root:mysql80@localhost:3306/k_car_navigator"
    return create_engine(db_url)

def get_vehicle_data_from_db():
    engine = get_db_engine()
    
    # 여러 테이블을 JOIN하여 필요한 정보를 한 번에 가져옵니다.
    query = """
    SELECT 
        v.registration_date AS 등록월,
        c.name AS 차량종류,
        r.name AS 시도,
        d.name AS 시군구,
        v.vehicles AS 등록차량수
    FROM vehicle_registration_status v
    LEFT JOIN vehicle_table c ON v.type = c.code
    LEFT JOIN region r ON v.region = r.code
    LEFT JOIN district d ON v.district = d.code
    """
    return pd.read_sql(query, engine)