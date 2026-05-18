import pandas as pd
from pathlib import Path

# 엑셀 파일들이 들어있는 폴더
excel_dir = Path("C:\python_workspace\pjoject\parsing\excel_files")

# SQL 저장 파일
car_type_file = "car_type_insert.sql"
district_sql_file = "district_insert.sql"
status_sql_file = "vehicle_registration_status_insert.sql"

sheet_name = "02.통계표_시군구"

car_type_columns = {
    "01": 5,   # 승용
    "02": 9,   # 승합
    "03": 13,  # 화물
    "04": 17   # 특수
}

car_type_sql_file = "car_type_insert.sql"

car_type_names = {
    "01": "승용",
    "02": "승합",
    "03": "화물",
    "04": "특수"
}

with open(car_type_sql_file, "w", encoding="utf-8") as f:
    f.write("USE car_db;\n\n")

    for code, name in car_type_names.items():
        f.write(
            "INSERT IGNORE INTO vehicle_type (code, name) "
            f"VALUES ('{code}', '{name}');\n"
        )

all_base = []
all_status = []

# 폴더 안의 모든 xlsx 파일 반복
for file_path in excel_dir.glob("*.xlsx"):

    print(f"처리 중: {file_path}")

    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None,
        engine="openpyxl"
    )

    registration_date = str(df.iloc[1, 1]).replace(".", "-") + "-01"

    df[0] = df[0].ffill()
    data_df = df.iloc[4:].copy()

    base = data_df[[0, 1]].copy()
    base.columns = ["시도", "시군구"]
    base = base.dropna(subset=["시도", "시군구"])
    base = base[base["시군구"] != "계"]
    base = base.drop_duplicates().reset_index(drop=True)

    all_base.append(base)

    for idx in range(4, len(df)):
        row = df.iloc[idx]

        sido = row[0]
        sigungu = row[1]

        if pd.isna(sido) or pd.isna(sigungu):
            continue

        if sigungu == "계":
            continue

        for type_code, count_col in car_type_columns.items():
            vehicles = row[count_col]

            if pd.isna(vehicles):
                continue

            all_status.append({
                "registration_date": registration_date,
                "시도": sido,
                "시군구": sigungu,
                "type": type_code,
                "vehicles": int(vehicles)
            })

# 전체 파일의 시도/시군구 합치기
base_df = pd.concat(all_base, ignore_index=True)
base_df = base_df.drop_duplicates().reset_index(drop=True)

# region 코드 생성
regions = base_df[["시도"]].drop_duplicates().reset_index(drop=True)
regions["region_code"] = [
    str(i + 1).zfill(2) for i in range(len(regions))
]

# district 코드 생성
districts = base_df.merge(regions, on="시도", how="left")
districts["district_seq"] = districts.groupby("region_code").cumcount().add(1)
districts["district_code"] = (
    districts["region_code"] +
    districts["district_seq"].astype(str).str.zfill(2)
)

# 상태 데이터에 코드 붙이기
status_df = pd.DataFrame(all_status)

status_df = status_df.merge(
    regions,
    on="시도",
    how="left"
)

status_df = status_df.merge(
    districts[["시도", "시군구", "district_code"]],
    on=["시도", "시군구"],
    how="left"
)

import math

# 한 파일당 INSERT 개수
chunk_size = 5000

# 전체 개수
total_count = len(status_df)

# 파일 개수 계산
file_count = math.ceil(total_count / chunk_size)

print("전체 INSERT 개수:", total_count)
print("생성 파일 개수:", file_count)

# 5000개씩 나누어서 저장
for i in range(file_count):

    start_idx = i * chunk_size
    end_idx = start_idx + chunk_size

    chunk_df = status_df.iloc[start_idx:end_idx]

    file_name = f"vehicle_registration_status_insert_{i + 1}.sql"

    with open(file_name, "w", encoding="utf-8") as f:

        f.write("USE car_db;\n\n")

        for _, row in chunk_df.iterrows():

            f.write(
                "INSERT INTO vehicle_registration_status "
                "(type, registration_date, vehicles, region, district) "
                f"VALUES ('{row['type']}', "
                f"'{row['registration_date']}', "
                f"{row['vehicles']}, "
                f"'{row['region_code']}', "
                f"'{row['district_code']}');\n"
            )

    print(f"{file_name} 생성 완료")


print("시도 개수:", len(regions))
print("시군구 개수:", len(districts))
print("등록현황 INSERT 개수:", len(status_df))
print("SQL 파일 생성 완료")