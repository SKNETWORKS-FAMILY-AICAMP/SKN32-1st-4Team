'''
entities.py
- DB 테이블을 기반으로 한 모든 엔티티 클래스 정의
- 각 클래스는 @dataclass를 사용하여 간결하게 작성됨
'''
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional

@dataclass
class FaqEntity:
    id: int
    company_id: int
    category_id: Optional[int]
    question: str
    answer: str
    created_at: datetime

@dataclass
class CompanyEntity:
    id: int
    name: str
    created_at: datetime

@dataclass
class CategoryEntity:
    id: int
    company_id: int
    name: str
    display_order: int
    created_at: datetime

@dataclass
class VehicleTypeEntity:
    code: str  # CHAR(2)
    name: str

@dataclass
class RegionEntity:
    code: str  # CHAR(2)
    name: str

@dataclass
class DistrictEntity:
    code: str  # CHAR(4)
    region_code: str  # CHAR(2)
    name: str

@dataclass
class VehicleRegistrationStatusEntity:
    pk: int
    type: str  # CHAR(2)
    registration_date: date
    vehicles: int
    region: str  # CHAR(2)
    district: str  # CHAR(2)