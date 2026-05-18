from typing import Optional, Dict, List, Tuple, Any


class SqlQueryBuilder:
    """
    안전한 동적 SQL Query Builder

    지원 기능:
    - WHERE
    - LIKE 검색
    - ORDER BY
    - LIMIT / OFFSET
    - COUNT QUERY

    특징:
    - 파라미터 바인딩
    - 중복 로직 제거
    """

    ALLOWED_ORDER_DIRECTIONS = {"ASC", "DESC"}

    # =========================================================
    # 내부 유틸
    # =========================================================

    def _normalize_like_values(
        self,
        values: Optional[list | str]
    ) -> List[str]:

        if values is None:
            return []

        if isinstance(values, str):
            return [values]

        return [v for v in values if v]

    # =========================================================
    # WHERE
    # =========================================================

    def build_where_clause(
        self,
        filters: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, Any]]:

        clauses = []
        params = {}

        for column, value in filters.items():

            if value is None:
                continue

            param_key = f"where_{column}"

            clauses.append(f"{column} = :{param_key}")
            params[param_key] = value

        return clauses, params

    # =========================================================
    # LIKE
    # =========================================================

    def build_like_clause(
        self,
        likes: Optional[List[Tuple[str, Optional[list | str]]]]
    ) -> Tuple[List[str], Dict[str, Any]]:

        clauses = []
        params = {}

        if not likes:
            return clauses, params

        for column, values in likes:

            normalized_values = self._normalize_like_values(values)
            if not normalized_values:
                continue

            # 각 키워드별로 LIKE 절 생성
            for idx, value in enumerate(normalized_values):
                param_key = f"{column}_like_{idx}"
                # 개별 조건들을 괄호 없이 일단 clauses에 다 넣거나, 컬럼별이 아닌 전체를 OR 처리
                clauses.append(f"{column} LIKE :{param_key}")
                params[param_key] = f"%{value}%"

        # [수정 포인트] 개별 컬럼들을 AND로 묶지 않도록 
        # build_conditions 쪽에 단일 대괄호 덩어리로 넘겨주기 위해 한 번 더 묶어줍니다.
        if clauses:
            return ["(" + " OR ".join(clauses) + ")"], params
            
        return clauses, params

    # =========================================================
    # ORDER BY
    # =========================================================

    def build_order_clause(
        self,
        orders: Optional[List[Tuple[str, Optional[str]]]]
    ) -> str:

        if not orders:
            return ""

        order_clauses = []

        for column, direction in orders:

            direction = (direction or "ASC").upper()

            if direction not in self.ALLOWED_ORDER_DIRECTIONS:
                direction = "ASC"

            order_clauses.append(
                f"{column} {direction}"
            )

        if not order_clauses:
            return ""

        return "ORDER BY " + ", ".join(order_clauses)

    # =========================================================
    # LIMIT OFFSET
    # =========================================================

    def build_limit_offset(
        self,
        page: int,
        size: int,
        get_pages: bool = True
    ) -> str:

        if not get_pages:
            return ""

        page = max(page, 1)
        size = max(size, 1)

        offset = (page - 1) * size

        return f"LIMIT {size} OFFSET {offset}"

    # =========================================================
    # 공통 WHERE 조립
    # =========================================================

    def build_conditions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        likes: Optional[List[Tuple[str, Optional[list | str]]]] = None
    ) -> Tuple[str, Dict[str, Any]]:

        filters = filters or {}

        all_clauses = []
        all_params = {}

        # WHERE
        where_clauses, where_params = self.build_where_clause(filters)
        all_clauses.extend(where_clauses)
        all_params.update(where_params)

        # LIKE
        like_clauses, like_params = self.build_like_clause(likes)
        all_clauses.extend(like_clauses)
        all_params.update(like_params)

        if not all_clauses:
            return "", all_params

        where_sql = " WHERE " + " AND ".join(all_clauses)

        return where_sql, all_params

    # =========================================================
    # SELECT QUERY
    # =========================================================

    def build_full_query(
        self,
        base_sql: str,
        filters: Optional[Dict[str, Any]] = None,
        likes: Optional[List[Tuple[str, Optional[list | str]]]] = None,
        orders: Optional[List[Tuple[str, Optional[str]]]] = None,
        page: int = 1,
        size: int = 10,
        get_pages: bool = True,
    ) -> Tuple[str, Dict[str, Any]]:

        query = base_sql.strip()

        # WHERE
        where_sql, params = self.build_conditions(
            filters=filters,
            likes=likes,
        )

        query += where_sql

        # ORDER BY
        order_sql = self.build_order_clause(orders)

        if order_sql:
            query += f" {order_sql}"

        # LIMIT OFFSET
        limit_sql = self.build_limit_offset(
            page=page,
            size=size,
            get_pages=get_pages,
        )

        if limit_sql:
            query += f" {limit_sql}"

        return query, params

    # =========================================================
    # COUNT QUERY
    # =========================================================

    def build_count_query(
        self,
        table_name: str,
        filters: Optional[Dict[str, Any]] = None,
        likes: Optional[List[Tuple[str, Optional[list | str]]]] = None,
    ) -> Tuple[str, Dict[str, Any]]:

        query = f"SELECT COUNT(*) FROM {table_name}"

        where_sql, params = self.build_conditions(
            filters=filters,
            likes=likes,
        )

        query += where_sql

        return query, params