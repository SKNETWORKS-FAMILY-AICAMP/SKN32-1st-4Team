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
        res = self.__db_service.select_vehicle_registration_status(param)

        dashboard_dto_from_table = [
            Mapper.to_dto(row, VehicleRegistrationStatusDTO)
            for row in res
        ]

        return dashboard_dto_from_table

    def get_vehicle_type(self):
        return self.__db_service.select_vehicle_type(VehicleTypeSearchDTO(order_clauses=[("code", None)]))
    
    def get_region(self):
        return self.__db_service.select_region(RegionSearchDTO(order_clauses=[("code", None)]))
    
    def get_district(self):
        return self.__db_service.select_district(DistrictSearchDTO(order_clauses=[("region_code", None), ("code", None)]))
