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
-> 테이블생성 

-> vehicle_type_insert.sql
region_insert.sql
district_insert.sql
vehicle_registration_status_insert.sql
순차 실행


 분할 sql
 
vehicle_registration_status_insert_1.sql
vehicle_registration_status_insert_2.sql
vehicle_registration_status_insert_3.sql
vehicle_registration_status_insert_4.sql
vehicle_registration_status_insert_5.sql
vehicle_registration_status_insert_6.sql
vehicle_registration_status_insert_7.sql
vehicle_registration_status_insert_8.sql
vehicle_registration_status_insert_9.sql
vehicle_registration_status_insert_10.sql
vehicle_registration_status_insert_11.sql
vehicle_registration_status_insert_12.sql
vehicle_registration_status_insert_13.sql
vehicle_registration_status_insert_14.sql
vehicle_registration_status_insert_15.sql
vehicle_registration_status_insert_16.sql
vehicle_registration_status_insert.sql 파일 실행
-> 순서대로

------------