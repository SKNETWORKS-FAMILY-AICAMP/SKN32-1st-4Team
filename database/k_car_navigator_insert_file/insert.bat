@echo off
set EXCLUDE_FILE=vehicle_registration_status_insert.sql
set DB_USER=root
set DB_PASS=sql80
set DB_NAME=K_Car_Navigator

for %%f in (*.sql) do (
    if not "%%f"=="%EXCLUDE_FILE%" (
        echo Running %%f ...
        mysql -u %DB_USER% -p%DB_PASS% --default-character-set=utf8mb4 %DB_NAME% < "%%f" 
    )
)
pause