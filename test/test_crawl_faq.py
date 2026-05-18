from common.logger import logger
from database.db_service import DBService
from crawling.crawling_faq import HYUNDAI, KIA, BMW
from service.crawl_service import CrawlService

if __name__=='__main__':
    brand_list = [
                    '현대자동차',
                    '기아자동차',
                    'BMW'
                    ]
    type_list = [
                    HYUNDAI, 
                    KIA,
                    BMW
                    ]
    for brand_name, brand_type in zip(brand_list, type_list):
        try:
            d = DBService()
            cid = d.insert_company_info(brand_name)
            cs = CrawlService()
            output_filename = cs.start_faq_crwaling(brand_type=brand_type, company_id=cid)
            result = cs.insert_faqs_from_json_file(output_filename, brand_name)
        except Exception as e:
            logger.error(f"{brand_name} 처리 중 오류 발생: {e}")
    