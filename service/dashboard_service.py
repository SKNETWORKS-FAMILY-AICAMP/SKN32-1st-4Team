import json
from common.logger import logger
from common.mapper import Mapper
from crawling.crawling_faq import FAQCrawler
from database.db_service import DBService
from models.dtos import VehicleRegistrationStatusDTO
from models.models import VehicleRegistrationStatusSearchDTO, VehicleTypeSearchDTO, RegionSearchDTO, DistrictSearchDTO

class DashboardService():
    def __init__(self, ):
        self.__db_service = DBService()

    def search_dashboard_by_param(self, param :VehicleRegistrationStatusSearchDTO):
        res_list, total_count = self.__db_service.select_vehicle_registration_status(param)

        dashboard_dto_from_table = [
            Mapper.to_dto(row, VehicleRegistrationStatusDTO)
            for row in res_list
        ]

        return dashboard_dto_from_table, total_count

    def get_vehicle_type(self):
        return self.__db_service.select_vehicle_type(VehicleTypeSearchDTO(order_clauses=[("code", None)]))
    
    def get_region(self):
        return self.__db_service.select_region(RegionSearchDTO(order_clauses=[("code", None)]))
    
    def get_district(self):
        return self.__db_service.select_district(DistrictSearchDTO(order_clauses=[("region_code", None), ("code", None)]))


    # FIXME: 필히 수정해야 함
    def get_vehicle_data_from_db(self,):
        return self.__db_service.get_vehicle_data_from_db()