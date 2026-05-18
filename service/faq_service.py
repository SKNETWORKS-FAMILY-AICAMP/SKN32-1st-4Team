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
            db_param = FaqSearchDTO(
                faq_id=param.faq_id,
                company_id=param.company_id,
                category_id=param.category_id,
                question=param.question,
                answer=param.answer,
                created_at=param.created_at,
                order_clauses=param.order_clauses,
            )
            res = self.__db_service.select_faq(db_param)
            keyword_lower = keyword.casefold()
            res = [
                faq for faq in res
                if keyword_lower in faq.question.casefold()
                or keyword_lower in faq.answer.casefold()
            ]
            count = len(res)

            if param.get_pages:
                start = (param.page - 1) * param.size
                end = start + param.size
                res = res[start:end]
        else:
            res = self.__db_service.select_faq(param)

            filter = Mapper.dto_to_dict(param)
            filter.pop('page', None)
            filter.pop('size', None)
            filter.pop('get_pages', None)
            filter.pop('total_size', None)
            filter.pop('order_clauses', None)
            filter.pop('keyword', None)

            count = self.__db_service.get_count_rows('faq', filter)

        faq_dto_from_table = [
            Mapper.to_dto(
                row,
                FaqDTO,
            )
            for row in res
        ]

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
