import json
from common.logger import logger
from common.mapper import Mapper
from crawling.crawling_faq import FAQCrawler
from database.db_service import DBService
from models.dtos import FaqDTO
from models.models import FaqSearchDTO

class FAQService():
    def __init__(self, ):
        self.__db_service = DBService()

    def search_faq_by_param(self, param :FaqSearchDTO):
        res = self.__db_service.select_faq(param)

        faq_dto_from_table = [
            Mapper.to_dto(
                row,
                FaqDTO,
            )
            for row in res
        ]

        filter = Mapper.dto_to_dict(param)
        del filter['page']
        del filter['size']
        del filter['get_pages']
        del filter['total_size']
        
        count = self.__db_service.get_count_rows('faq', filter)

        return faq_dto_from_table, count