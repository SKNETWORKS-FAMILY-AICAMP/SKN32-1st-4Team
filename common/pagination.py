from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# 기본 페이징 DTO
@dataclass
class PagingDTO:
    page: int = 1
    size: int = 10
    total_size: int = 0