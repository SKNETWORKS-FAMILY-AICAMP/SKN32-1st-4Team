'''
dto.py
각 DTO 클래스는 DB 테이블 구조를 기준으로 작성.
필요한 경우, 편하게 필드를 수정하거나 생략 가능.
'''
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class FaqDTO:
    question: str
    answer: str
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    fid: Optional[int] = None
    company_id: Optional[int] = None


@dataclass
class CompanyDTO:
    id: Optional[int] = None
    name: Optional[str] = None


@dataclass
class CategoryDTO:
    id: int
    company_id: int
    name: str
    display_order: int
    
