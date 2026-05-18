from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parents[1]))

from service.dashboard_service import DashboardService
from models.models import VehicleRegistrationStatusSearchDTO

d = DashboardService()

# 차량 현황 조회
res_list, total_count = d.search_dashboard_by_param(
    VehicleRegistrationStatusSearchDTO(
                    type= ['01'] # 차량 종류
                    # , region= ['02','04', '05'] # 시/도
                    # , district= ['0501', '0502'] # 시/군/구
                    # , registration_date= [datetime(2020, 4, 1), datetime(2023, 12, 1)] # 등록 월 
                    # 등록 월 의 경우 일까지 저장되어 있음 (e.g. 2026-04-01)
                    # (DB 에서는 월만 저장하는 타입은 없기 때문에 무조건 -01 추가 해야함)
                    # ,get_pages=True
                 )
)
print(len(res_list), total_count)

# for vrs in res_list:
    # print(vrs.type, vrs.vehicles)

# 차량 타입 조회
res_get_list = d.get_vehicle_type()
print(len(res_get_list), res_get_list)

# 시/도 조회
res_region_list = d.get_region()
print(len(res_region_list), res_region_list)

# 시/군/구 조회
res_district_list = d.get_district()
print(len(res_district_list), res_district_list[:4], res_district_list[28:34])