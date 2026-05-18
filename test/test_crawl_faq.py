import os
import tempfile
import zipfile
from pathlib import Path

from common.logger import logger
from database.db_service import DBService
from service.crawl_service import CrawlService


FAQ_BACKUP_FILES = [
    ("현대자동차", "HYUNDAI_1_faq.json"),
    ("기아자동차", "KIA_2_faq.json"),
    ("BMW", "BMW_3_faq.json"),
]


def get_backup_zip_path():
    return Path(
        os.getenv(
            "FAQ_BACKUP_ZIP",
            r"C:\Users\User\Downloads\data_backup.zip",
        )
    )


def load_faq_backup_to_db():
    backup_zip_path = get_backup_zip_path()
    if not backup_zip_path.exists():
        raise FileNotFoundError(f"FAQ 백업 파일을 찾을 수 없습니다: {backup_zip_path}")

    db_service = DBService()
    crawl_service = CrawlService()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(backup_zip_path) as backup_zip:
            backup_zip.extractall(temp_path)

        for company_name, file_name in FAQ_BACKUP_FILES:
            try:
                db_service.insert_company_info(company_name)

                # 크롤링을 다시 하지 않고 백업 JSON 파일을 DB에 적재한다.
                # output_filename = crawl_service.start_faq_crwaling(...)
                output_filename = temp_path / file_name
                result = crawl_service.insert_faqs_from_json_file(
                    str(output_filename),
                    company_name,
                )
                logger.info(f"[*] {company_name} FAQ 적재 완료: {len(result)}건")
            except Exception as error:
                logger.error(f"{company_name} 처리 중 오류 발생: {error}")


if __name__ == "__main__":
    load_faq_backup_to_db()
