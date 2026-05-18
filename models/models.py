from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from common.pagination import PagingDTO

@dataclass
class CrawlItem:
    company_id: int
    category_name: str
    display_order : int
    question: str
    answer: str


@dataclass
class FaqSearchDTO(PagingDTO):
    get_pages: bool = False
    order_clauses: Optional[List[Tuple[str, Optional[str]]]] = None
    faq_id: Optional[int] = None
    company_id: Optional[int] = None
    category_id: Optional[int] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class CategorySearchDTO(PagingDTO):
    get_pages: bool = False
    order_clauses: Optional[List[Tuple[str, Optional[str]]]] = None
    category_id: Optional[int] = None
    company_id: Optional[int] = None
    category_name: Optional[int] = None

    
@dataclass
class CompanySearchDTO(PagingDTO):
    get_pages: bool = False
    order_clauses: Optional[List[Tuple[str, Optional[str]]]] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None