import pandas as pd
from pathlib import Path

excel_dir = Path(r"C:\python_workspace\parsing\excel_files")
sheet_name = "02.통계표_시군구"
db_name = "k_car_navigator"

vehicle_type_columns = {
    "01": ("승용", 5),
    "02": ("승합", 9),
    "03": ("화물", 13),
    "04": ("특수", 17)
}

def normalize_name(value):
    return str(value).strip().replace(" ", "")

def find_existing_region_key(region_keys, sido, sigungu):
    current_key = f"{sido}-{sigungu}"

    for key in region_keys:
        if not key.startswith(f"{sido}-"):
            continue

        if current_key in key or key in current_key:
            return key

    return None

all_data = []
region_district_data = []
region_keys = []

excel_files = list(excel_dir.glob("*.xlsx"))

if not excel_files:
    print("엑셀 파일이 없습니다.")
    exit()

for file_path in excel_files:
    print(f"읽는 파일: {file_path.name}")

    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None,
        engine="openpyxl"
    )

    registration_date = str(df.iloc[1, 1]).replace(".", "-") + "-01"

    df[0] = df[0].ffill()

    for idx in range(4, len(df)):
        row = df.iloc[idx]

        sido = row[0]
        sigungu = row[1]

        if pd.isna(sido) or pd.isna(sigungu):
            continue

        sido = normalize_name(sido)
        sigungu = normalize_name(sigungu)

        if sigungu == "계":
            continue

        existing_key = find_existing_region_key(region_keys, sido, sigungu)

        if existing_key:
            final_sido, final_sigungu = existing_key.split("-", 1)
        else:
            final_sido = sido
            final_sigungu = sigungu
            new_key = f"{final_sido}-{final_sigungu}"
            region_keys.append(new_key)

            region_district_data.append({
                "시도": final_sido,
                "시군구": final_sigungu
            })

        for type_code, (type_name, count_col) in vehicle_type_columns.items():
            vehicles = row[count_col]

            if pd.isna(vehicles):
                continue

            all_data.append({
                "registration_date": registration_date,
                "type_code": type_code,
                "type_name": type_name,
                "vehicles": int(vehicles),
                "시도": final_sido,
                "시군구": final_sigungu
            })

base_df = pd.DataFrame(region_district_data)
base_df = base_df.drop_duplicates().reset_index(drop=True)

regions = base_df[["시도"]].drop_duplicates().reset_index(drop=True)
regions["region_code"] = [
    str(i + 1).zfill(2) for i in range(len(regions))
]

districts = base_df.merge(regions, on="시도", how="left")
districts["district_seq"] = districts.groupby("region_code").cumcount().add(1)

districts["district_code"] = (
    districts["region_code"] +
    districts["district_seq"].astype(str).str.zfill(2)
)

status_df = pd.DataFrame(all_data)

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

with open("vehicle_type_insert.sql", "w", encoding="utf-8") as f:
    f.write(f"USE {db_name};\n\n")

    for type_code, (type_name, _) in vehicle_type_columns.items():
        f.write(
            "INSERT IGNORE INTO vehicle_type (code, name) "
            f"VALUES ('{type_code}', '{type_name}');\n"
        )

with open("region_insert.sql", "w", encoding="utf-8") as f:
    f.write(f"USE {db_name};\n\n")

    for _, row in regions.iterrows():
        f.write(
            "INSERT IGNORE INTO region (code, name) "
            f"VALUES ('{row['region_code']}', '{row['시도']}');\n"
        )

with open("district_insert.sql", "w", encoding="utf-8") as f:
    f.write(f"USE {db_name};\n\n")

    for _, row in districts.iterrows():
        f.write(
            "INSERT IGNORE INTO district (code, region_code, name) "
            f"VALUES ('{row['district_code']}', "
            f"'{row['region_code']}', "
            f"'{row['시군구']}');\n"
        )

# vehicle_registration_status_insert.sql 5000개씩 분할 저장
chunk_size = 5000
total_count = len(status_df)
file_index = 1

for start_idx in range(0, total_count, chunk_size):
    end_idx = start_idx + chunk_size
    chunk_df = status_df.iloc[start_idx:end_idx]

    file_name = f"vehicle_registration_status_insert_{file_index}.sql"

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"USE {db_name};\n\n")

        for _, row in chunk_df.iterrows():
            f.write(
                "INSERT INTO vehicle_registration_status "
                "(type, registration_date, vehicles, region, district) "
                f"VALUES ('{row['type_code']}', "
                f"'{row['registration_date']}', "
                f"{row['vehicles']}, "
                f"'{row['region_code']}', "
                f"'{row['district_code']}');\n"
            )

    print(f"{file_name} 생성 완료")
    file_index += 1

print("vehicle_type_insert.sql 생성 완료")
print("region_insert.sql 생성 완료")
print("district_insert.sql 생성 완료")
print("vehicle_registration_status_insert 분할 생성 완료")

print("읽은 엑셀 파일 수:", len(excel_files))
print("시도 개수:", len(regions))
print("시군구 개수:", len(districts))
print("등록현황 개수:", len(status_df))
print("분할 SQL 파일 개수:", file_index - 1)