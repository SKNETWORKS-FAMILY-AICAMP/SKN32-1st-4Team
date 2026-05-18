from typing import Optional, Dict, List, Tuple

class SqlQueryBuilder():
    """
    동적 SQL 빌더: WHERE, ORDER BY, LIMIT/OFFSET
    """
    
    def build_where_clause(self, filters: dict) -> Tuple[List[str], Dict]:
        '''
        filters 딕셔너리를 기반으로 SQL WHERE 절과 파라미터를 동적으로 생성

        return:
            where_clauses (list): ["name = :name", ...]
            params (dict): {"name": value, ...}
        '''
        where_clauses = []
        params = {}

        # None이 아닌 값만 조건으로 추가
        for key, value in filters.items():
            if value is not None:
                where_clauses.append(f"{key} = :{key}")
                params[key] = value

        return where_clauses, params
    
    def build_order_clause(self, orders: list[tuple]) -> str:
        """
        orders: 정렬할 컬럼과 방향을 순서대로 받음
            예: [("created_at", "DESC"), ("faq_id", "ASC")]

        return:
            order_clause (str): "ORDER BY created_at DESC, faq_id ASC"
        """
        order_clauses = []

        for col, direction in orders:
            if not direction:
                direction = "ASC"  # 기본값
            dir_upper = direction.upper()
            if dir_upper not in ["ASC", "DESC"]:
                dir_upper = "ASC"  # 안전장치
            order_clauses.append(f"{col} {dir_upper}")

        if order_clauses:
            return "ORDER BY " + ", ".join(order_clauses)
        else:
            return "" 
        
    def build_limit_offset(self, page: int, size: int, get_pages: bool) -> str:
        """
        LIMIT/OFFSET SQL 생성
        get_pages: True면 페이징 적용, False면 전체 조회
        """
        if get_pages:
            offset = (page - 1) * size
            return f"LIMIT {size} OFFSET {offset}"
        return ""

    def build_full_query(self, base_sql: str, filters: Dict, orders: List[Tuple[str, Optional[str]]],
                         page: int = 1, size: int = 10, get_pages: bool = True) -> Tuple[str, Dict]:
        """
        전체 SQL 빌드: WHERE + ORDER BY + LIMIT/OFFSET
        """
        where_clauses, params = self.build_where_clause(filters)
        if where_clauses:
            base_sql += " WHERE " + " AND ".join(where_clauses)

        order_sql = self.build_order_clause(orders)
        if order_sql:
            base_sql += " " + order_sql

        limit_sql = self.build_limit_offset(page, size, get_pages)
        if limit_sql:
            base_sql += " " + limit_sql

        return base_sql, params
    
    def build_count_query(self, table_name: str, filters: Dict,) -> Tuple[str, Dict]:
        """
        Count SQL 빌드
        """
        base_sql = "SELECT * FROM "+table_name
        where_clauses, params = self.build_where_clause(filters)
        if where_clauses:
            base_sql += " WHERE " + " AND ".join(where_clauses)

        return base_sql, params