from common.logger import logger
from alive_progress import alive_bar
from sqlalchemy import text
from database.db import get_engine
from common.sql_query_builder import SqlQueryBuilder
from common.mapper import Mapper
from models.entities import *
from models.models import *


class DBService(SqlQueryBuilder):
    def __init__(self):
        # DB 연결 엔진 생성
        self.engine = get_engine()

        # 회사 ID 조회용 SQL
        self.sql_select_company_id = "SELECT id FROM company WHERE name = :company_name"


    def insert_company_info(self, company_name) -> int:
        '''
        회사 정보가 없으면 INSERT, 있으면 기존 ID 조회 후 반환
        '''
        with self.engine.begin() as conn:
            company_result = self.select_company(param_dto=CompanySearchDTO(company_name=company_name))

            # 이미 존재하는 경우
            if company_result:
                company_id = company_result[0].id

            # 존재하지 않으면 새로 INSERT
            else:
                insert_sql = '''
                INSERT INTO company (name)
                VALUES (:company_name)
                '''

                result = conn.execute(
                    text(insert_sql),
                    {"company_name": company_name}
                )

                # insert된 PK
                company_id = result.lastrowid

            logger.info(f"[*] 회사 매핑 완료 - {company_name} (ID: {company_id})")

            return company_id
   

    def insert_category_to_db(self, company_id, cat_name, display_order) -> int:
        '''
        category 존재 여부 확인 후 없으면 INSERT 후 ID 반환
        '''
        with self.engine.begin() as conn:
            cat_result = self.select_category(CategorySearchDTO(company_id=company_id, category_name=cat_name))

            # 이미 존재하면 기존 ID 사용
            if cat_result:
                category_id = cat_result[0].id

            # 없으면 신규 생성
            else:
                insert_sql = '''
                INSERT INTO category (company_id, name, display_order)
                VALUES (:company_id, :name, :display_order)
                '''

                result = conn.execute(
                    text(insert_sql),
                    {
                        "company_id": company_id,
                        "name": cat_name,
                        "display_order": display_order,
                    }
                )

                category_id = result.lastrowid

            return category_id

    def select_company(self, param_dto:CompanySearchDTO = CompanySearchDTO()) -> list[CompanyEntity]:
        '''
        조건 기반 회사 조회
        '''
        base_sql = "SELECT id, name, created_at FROM company"
        filters = {
            "id": param_dto.company_id,
            "name": param_dto.company_name,
        }

        sql, params = self.build_full_query(
            base_sql=base_sql,
            filters=filters,
            orders=param_dto.order_clauses or [],
            page=param_dto.page,
            size=param_dto.size,
            get_pages=param_dto.get_pages
        )

        with self.engine.begin() as conn:
            rows = conn.execute(text(sql), params).fetchall()

        # Entity로 변환
        return [Mapper.to_entity(row, CompanyEntity) for row in rows]

    def select_category(self, param_dto:CategorySearchDTO = CategorySearchDTO()) -> list[CategoryEntity]:
        '''
        조건 기반 카테고리 조회
        '''
        base_sql = "SELECT id, company_id, name, display_order, created_at FROM category"
        filters = {
            "id": param_dto.category_id,
            "company_id": param_dto.company_id,
            "name": param_dto.category_name,
        }

        sql, params = self.build_full_query(
            base_sql=base_sql,
            filters=filters,
            orders=param_dto.order_clauses or [],
            page=param_dto.page,
            size=param_dto.size,
            get_pages=param_dto.get_pages
        )

        with self.engine.begin() as conn:
            rows = conn.execute(text(sql), params).fetchall()

        # Entity로 변환
        return [Mapper.to_entity(row, CategoryEntity) for row in rows]

    def select_faq(self, param_dto:FaqSearchDTO = FaqSearchDTO()) -> list[FaqEntity]:
        '''
        조건 기반 FAQ 조회
        '''
        base_sql = "SELECT id, company_id, category_id, question, answer, created_at FROM faq"
        filters = {
            "id": param_dto.faq_id,
            "company_id": param_dto.company_id,
            "category_id": param_dto.category_id,
            "question": param_dto.question,
            "answer": param_dto.answer,
        }

        sql, params = self.build_full_query(
            base_sql=base_sql,
            filters=filters,
            orders=param_dto.order_clauses or [],
            page=param_dto.page,
            size=param_dto.size,
            get_pages=param_dto.get_pages
        )

        with self.engine.begin() as conn:
            rows = conn.execute(text(sql), params).fetchall()

        # Entity로 변환
        return [Mapper.to_entity(row, FaqEntity) for row in rows]
    
    def get_count_rows(self, table_name, filters) -> int:
        count_sql, count_params = self.build_count_query(
            table_name=table_name,
            filters=filters
        )
        with self.engine.begin() as conn:
            count = conn.execute(text(count_sql), count_params).scalar()
        
        return count if count is not None else 0
    

    def insert_faq_to_db(self, company_id, faq_list):
        '''
        FAQ 리스트를 DB에 저장 (카테고리 포함 + 중복 체크 포함)
        '''
        with self.engine.begin() as conn:

            success_count = 0  # 신규 저장 수
            skip_count = 0     # 중복으로 스킵된 수
            result_faq_id_list = []

            # 카테고리 캐싱 (DB 조회 최소화)
            category_cache = {}

            with alive_bar(len(faq_list)) as bar:
                for item in faq_list:
                    cat_name = item['category_name']
                    display_order = item['display_order']
                    question = item['question']
                    answer = item['answer']

                    # 카테고리 ID 캐싱 처리
                    if cat_name in category_cache:
                        category_id = category_cache[cat_name]
                    else:
                        category_id = self.insert_category_to_db(
                            company_id, cat_name, display_order
                        )
                        category_cache[cat_name] = category_id

                    # 중복 FAQ 체크
                    entities = self.select_faq(FaqSearchDTO(
                        company_id=company_id,
                        category_id=category_id,
                        question=question
                    ))

                    # 이미 존재하면 스킵
                    if entities:
                        skip_count += 1
                        continue

                    # FAQ INSERT
                    insert_sql = '''
                    INSERT INTO faq (company_id, category_id, question, answer)
                    VALUES (:company_id, :category_id, :question, :answer)
                    '''

                    result = conn.execute(
                        text(insert_sql),
                        {
                            "company_id": company_id,
                            "category_id": category_id,
                            "question": question,
                            "answer": answer,
                        }
                    )

                    faq_id = result.lastrowid
                    result_faq_id_list.append(faq_id)
                    success_count += 1

                    # progress bar 증가
                    bar()

            # 결과 리포트 출력
            logger.info("==============================================")
            logger.info(f"[*] DB 적재 완료 리포트 - 신규 저장 성공: {success_count}건 - 기존 중복 패스: {skip_count}건")
            logger.info("==============================================")

            return result_faq_id_list