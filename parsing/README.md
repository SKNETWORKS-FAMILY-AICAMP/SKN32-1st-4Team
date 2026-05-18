# passing 

## 사용방법

pandas
openpyxl
pymysql

parsing
│
├── sample.xlsx
├── parsing.py
├── district_insert.sql
├── vehicle_registration_status_insert.sql
└── README.md


sample.xlsx
자동차 등록 현황 원본 엑셀 파일

python parsing.py
실행 후
->  district_insert.sql
    vehicle_registration_status_insert.sql 생성

테이블 생성 후 
vehicle_type INSERT
region INSERT
district_insert.sql 파일 실행
vehicle_registration_status_insert.sql 파일 실행
-> 순서대로

------------