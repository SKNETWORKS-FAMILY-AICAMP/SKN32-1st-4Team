import pandas as pd
import json
import pymysql

file_path = "sample.xlsx"

# 엑셀 읽기
df = pd.read_excel(
    file_path,
    sheet_name="02.통계표_시군구",
    header=None,
    engine="openpyxl"
)

# 조회년월 추출
search_date = str(df.iloc[1, 1]).replace(".", "-")

# 시도 컬럼 결측값 채우기
df[0] = df[0].ffill()

result = []

# 차량 타입별 "계" 컬럼
car_type_columns = {
    "승용": 5,
    "승합": 9,
    "화물": 13,
    "특수": 17
}

# 실제 데이터 시작 부분부터 반복
for idx in range(4, len(df)):

    row = df.iloc[idx]

    sido = row[0]
    sigungu = row[1]

    # 시군구가 비어있으면 스킵
    if pd.isna(sigungu):
        continue

    # 합계 행 제외
    if sigungu == "계":
        continue

    for car_type, count_col in car_type_columns.items():

        value = row[count_col]

        # 값이 없는 경우 제외
        if pd.isna(value):
            continue

        result.append({
            "조회년월": search_date,
            "시도": sido,
            "시군구": sigungu,
            "승용차타입": car_type,
            "차량수(계)": int(value)
        })

# JSON 출력
# print(json.dumps(
    result,
    ensure_ascii=False,
    indent=4
# ))



# # ------------------------------------------------------------------------------

import pandas as pd

file_path = "sample.xlsx"

df = pd.read_excel(
    file_path,
    sheet_name="02.통계표_시군구",
    header=None,
    engine="openpyxl"
)

df[0] = df[0].ffill()

data_df = df.iloc[4:].copy()

districts = data_df[[0, 1]].copy()
districts.columns = ["시도", "시군구"]

districts = districts.dropna(subset=["시도", "시군구"])
districts = districts[districts["시군구"] != "계"]
districts = districts.drop_duplicates().reset_index(drop=True)

regions = districts[["시도"]].drop_duplicates().reset_index(drop=True)
regions["region_code"] = [
    str(i + 1).zfill(2) for i in range(len(regions))
]

districts = districts.merge(regions, on="시도", how="left")

districts["district_seq"] = (
    districts.groupby("region_code")
    .cumcount()
    .add(1)
)

districts["district_code"] = (
    districts["region_code"] +
    districts["district_seq"].astype(str).str.zfill(2)
)

print("시도 개수:", len(regions))
print("시군구 개수:", len(districts))

with open("district_insert.sql", "w", encoding="utf-8") as f:
    f.write("USE car_db;\n\n")

    f.write("-- region insert\n")
    for _, row in regions.iterrows():
        f.write(
            "INSERT IGNORE INTO region (code, name) "
            f"VALUES ('{row['region_code']}', '{row['시도']}');\n"
        )

    f.write("\n-- district insert\n")
    for _, row in districts.iterrows():
        f.write(
            "INSERT IGNORE INTO district (code, region_code, name) "
            f"VALUES ('{row['district_code']}', "
            f"'{row['region_code']}', "
            f"'{row['시군구']}');\n"
        )

# print("district_insert.sql 파일 생성 완료")


# print(districts["시도"].value_counts())


file_path = "sample.xlsx"

df = pd.read_excel(
    file_path,
    sheet_name="02.통계표_시군구",
    header=None,
    engine="openpyxl"
)

# 조회년월: 2026.04 -> 2026-04-01
registration_date = str(df.iloc[1, 1]).replace(".", "-") + "-01"

df[0] = df[0].ffill()

data_df = df.iloc[4:].copy()

car_type_columns = {
    "01": 5,   # 승용
    "02": 9,   # 승합
    "03": 13,  # 화물
    "04": 17   # 특수
}

# region 코드 생성
base = data_df[[0, 1]].copy()
base.columns = ["시도", "시군구"]
base = base.dropna(subset=["시도", "시군구"])
base = base[base["시군구"] != "계"]
base = base.drop_duplicates().reset_index(drop=True)

regions = base[["시도"]].drop_duplicates().reset_index(drop=True)
regions["region_code"] = [
    str(i + 1).zfill(2) for i in range(len(regions))
]

districts = base.merge(regions, on="시도", how="left")
districts["district_seq"] = districts.groupby("region_code").cumcount().add(1)
districts["district_code"] = (
    districts["region_code"] +
    districts["district_seq"].astype(str).str.zfill(2)
)

result = []

for idx in range(4, len(df)):
    row = df.iloc[idx]

    sido = row[0]
    sigungu = row[1]

    if pd.isna(sido) or pd.isna(sigungu):
        continue

    if sigungu == "계":
        continue

    matched = districts[
        (districts["시도"] == sido) &
        (districts["시군구"] == sigungu)
    ]

    if matched.empty:
        continue

    region_code = matched.iloc[0]["region_code"]
    district_code = matched.iloc[0]["district_code"]

    for type_code, count_col in car_type_columns.items():
        vehicles = row[count_col]

        if pd.isna(vehicles):
            continue

        result.append({
            "type": type_code,
            "registration_date": registration_date,
            "vehicles": int(vehicles),
            "region": region_code,
            "district": district_code
        })

with open("vehicle_registration_status_insert.sql", "w", encoding="utf-8") as f:
    f.write("USE car_db;\n\n")

    for row in result:
        f.write(
            "INSERT INTO vehicle_registration_status "
            "(type, registration_date, vehicles, region, district) "
            f"VALUES ('{row['type']}', "
            f"'{row['registration_date']}', "
            f"{row['vehicles']}, "
            f"'{row['region']}', "
            f"'{row['district']}');\n"
        )

print("생성된 INSERT 개수:", len(result))
print("vehicle_registration_status_insert.sql 생성 완료")