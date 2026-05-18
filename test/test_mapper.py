# test_mapper.py
from datetime import datetime
from types import SimpleNamespace
from common.mapper import Mapper
from models.entities import FaqEntity
from models.dtos import FaqDTO

# --- 1. row_to_dict 테스트 ---
fake_row = SimpleNamespace(_mapping={
    "id": 1,
    "company_id": 100,
    "category_id": 5,
    "question": "테스트 질문",
    "answer": "테스트 답변",
    "created_at": datetime(2026, 5, 17)
})

row_dict = Mapper.row_to_dict(fake_row)
print("row_to_dict 결과:", row_dict)
# 예상: row._mapping 그대로 dict로 변환

# --- 2. to_entity 테스트 ---
faq_entity = Mapper.to_entity(fake_row, FaqEntity)
print("to_entity 결과:", faq_entity)
# 예상: FaqEntity(id=1, company_id=100, ...) 형태의 dataclass 객체

# --- 3. to_dto 테스트 ---
faq_dto = Mapper.to_dto(
    faq_entity,
    FaqDTO,
    # custom_map={"category_id": "category", "id": "fid"}
)
print("to_dto 결과:", faq_dto)
# 예상: FaqDTO(fid=1, company_id=100, category=5, question=..., answer=..., created_at=...)

# --- 4. dict 기반 to_dto 테스트 ---
faq_dict = {
    "id": 2,
    "company_id": 200,
    "category_id": 10,
    "question": "dict 기반 질문",
    "answer": "dict 기반 답변",
    "created_at": datetime(2026, 5, 17)
}
faq_dto_from_dict = Mapper.to_dto(
    faq_dict,
    FaqDTO,
    custom_map={"category_id": "category", "id": "fid"}
)
print("dict → DTO 결과:", faq_dto_from_dict)