import json
from common.logger import logger
from crawling.crawling_faq import FAQCrawler
from database.db_service import DBService
from models.dtos import CompanyDTO
from models.models import CompanySearchDTO

class CrawlService():
    def __init__(self, ):
        self.__db_service = DBService()
        self.faq_crwaler = FAQCrawler()

    def start_faq_crwaling(self, brand_type, company_id):
        self.faq_crwaler.set_brand_type(brand_type)
        return self.faq_crwaler.save_faq_crawled_data_to_json(company_id)

    def insert_faqs_from_json_file(self, json_file_path, company_name):
        '''
        JSON 파일을 읽어서 FAQ 데이터를 DB에 적재
        '''
        company_result = self.__db_service.select_company(param_dto=CompanySearchDTO(company_name=company_name))

        # 회사 ID 확보 (없으면 에러)
        if company_result:
            company_id = company_result[0].id
        else:
            logger.error(f"[!] '{company_name}' 회사가 존재하지 않습니다.")
            raise

        # JSON 파일 로드
        try:
            with open(json_file_path, "r", encoding="utf-8") as f:
                faq_list = json.load(f)
        except FileNotFoundError:
            logger.error(f"[!] '{json_file_path}' 파일이 존재하지 않습니다.")
            raise

        logger.info(f"[*] 총 {len(faq_list)}개의 데이터를 DB에 적재합니다.")

        # 실제 insert 수행
        return self.__db_service.insert_faq_to_db(company_id, faq_list)