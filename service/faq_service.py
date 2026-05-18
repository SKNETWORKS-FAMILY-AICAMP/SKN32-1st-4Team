import json
from common.logger import logger
from common.mapper import Mapper
from crawling.crawling_faq import FAQCrawler
from database.db_service import DBService
from models.dtos import FaqDTO
from models.models import CategorySearchDTO, FaqSearchDTO

class FAQService():
    def __init__(self, ):
        self.__db_service = DBService()

    @staticmethod
    def normalize_category_name(category_name):
        category_name = str(category_name or "").strip()
        if not category_name or category_name.casefold() == "web":
            return "기타"
        return category_name

    def search_faq_by_param(self, param :FaqSearchDTO):
        keyword = str(param.keyword or "").strip()
        if keyword:
            param.likes = [
                        ("question", [keyword]),
                        ("answer", [keyword])
                    ]
        res = self.__db_service.select_faq(param)

        faq_dto_from_table = [
            Mapper.to_dto(row, FaqDTO)
            for row in res
        ]

        # 1. DTO를 딕셔너리로 변환
        filter_dict = Mapper.dto_to_dict(param)
        
        # 2. WHERE 절 컬럼이 아닌 제어용/특수 필드들을 딕셔너리에서 제거
        likes_param = filter_dict.pop('likes', [])      # likes 꺼내고 제거
        orders_param = filter_dict.pop('order_clauses', []) # order_clauses가 있다면 제거
        
        # 페이징 관련 필드 제거 (pop을 쓰면 안전하게 지울 수 있습니다)
        for key in ['page', 'size', 'get_pages', 'total_size', 'keyword']:
            filter_dict.pop(key, None)
            
        count = self.__db_service.get_count_rows('faq', filters=filter_dict, likes=likes_param)

        return faq_dto_from_table, count

    def get_companies(self):
        return self.__db_service.select_company()

    def get_categories(self, company_id=None):
        categories = self.__db_service.select_category(
            CategorySearchDTO(company_id=company_id)
        )
        return sorted(
            categories,
            key=lambda category: (
                category.display_order,
                self.normalize_category_name(category.name),
            )
        )
