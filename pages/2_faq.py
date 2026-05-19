import streamlit as st

from models.models import FaqSearchDTO
from service.faq_service import FAQService


PAGE_SIZE = 20


def render_pagination(total_pages):
    if total_pages <= 1:
        return

    current_page = st.session_state.faq_page
    window_start = ((current_page - 1) // 5) * 5 + 1
    window_end = min(window_start + 4, total_pages)

    st.markdown(
        """
        <style>
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker) {
                align-items: center;
                gap: 0.2rem;
                justify-content: center;
                margin: 1.75rem auto 0.75rem;
                max-width: 36rem;
            }
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="stButton"] > button {
                background: transparent;
                border: 0;
                border-radius: 0;
                box-shadow: none;
                color: #7a7a7a;
                font-size: 1.55rem;
                height: 2.35rem;
                min-height: 2.35rem;
                min-width: 2.35rem;
                padding: 0 0.2rem;
            }
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="stButton"] > button:hover {
                border: 0;
                color: #222;
            }
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="stButton"] > button:disabled {
                background: transparent;
                color: #222;
                opacity: 1;
            }
            .faq-page-active {
                color: #222;
                display: block;
                font-size: 1.55rem;
                font-weight: 600;
                line-height: 2.35rem;
                margin: 0 auto;
                min-width: 2.35rem;
                text-align: center;
                width: fit-content;
            }
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="column"]:nth-child(2) button,
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="column"]:nth-child(3) button,
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="column"]:nth-last-child(2) button,
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="column"]:nth-last-child(3) button {
                border: 1px solid #d1d5db;
                color: #9ca3af;
                font-size: 1.7rem;
            }
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="column"]:nth-child(2) button:disabled,
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="column"]:nth-child(3) button:disabled,
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="column"]:nth-last-child(2) button:disabled,
            div[data-testid="stHorizontalBlock"]:has(.faq-pagination-marker)
                div[data-testid="column"]:nth-last-child(3) button:disabled {
                border: 1px solid #d1d5db;
                opacity: 0.35;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    page_numbers = list(range(window_start, window_end + 1))
    columns = st.columns([2.5, 0.45, 0.45, *([0.65] * len(page_numbers)), 0.45, 0.45, 2.5])
    columns[0].markdown("<span class='faq-pagination-marker'></span>", unsafe_allow_html=True)

    page_actions = [
        (columns[1], "《", 1, current_page <= 1),
        (columns[2], "‹", current_page - 1, current_page <= 1),
    ]
    number_columns = columns[3:-3]
    page_actions.extend(
        [
            (columns[-3], "›", current_page + 1, current_page >= total_pages),
            (columns[-2], "》", total_pages, current_page >= total_pages),
        ]
    )

    for column, label, page, disabled in page_actions:
        if column.button(label, disabled=disabled):
            st.session_state.faq_page = page
            st.rerun()

    for column, page in zip(number_columns, page_numbers):
        if page == current_page:
            column.markdown(
                f"<span class='faq-page-active'>{page}</span>",
                unsafe_allow_html=True,
            )
            continue

        if column.button(str(page)):
            st.session_state.faq_page = page
            st.rerun()


@st.cache_resource
def get_faq_service():
    return FAQService()


@st.cache_data(ttl=60)
def load_companies():
    faq_service = FAQService()
    return faq_service.get_companies()


@st.cache_data(ttl=60)
def load_categories(company_id):
    faq_service = FAQService()
    return faq_service.get_categories(company_id)


@st.cache_data(ttl=60)
def load_faq_page(company_id, category_id, keyword, page, size):
    faq_service = FAQService()
    return faq_service.search_faq_by_param(FaqSearchDTO(
        company_id=company_id,
        category_id=category_id,
        keyword=keyword or None,
        page=page,
        size=size,
        get_pages=True,
    ))


st.title("FAQ 센터")

try:
    get_faq_service()
    company_options = load_companies()
except Exception as error:
    st.error("DB에 연결할 수 없습니다. `.env`의 DB 설정과 MySQL 실행 상태를 확인해 주세요.")
    st.exception(error)
    st.stop()

st.sidebar.header("검색 조건")

company_name_by_id = {company.id: company.name for company in company_options}
company_ids = [None] + [company.id for company in company_options]
selected_company_id = st.sidebar.selectbox(
    "회사",
    company_ids,
    format_func=lambda company_id: (
        "전체" if company_id is None else company_name_by_id[company_id]
    ),
)

# 기존 방식: 회사 선택 변경 시 카테고리 재조회
# 개선 방식: 전체 카테고리 캐싱 후 메모리 필터링 사용
try:
    all_categories = load_categories(None)

    category_options = (
        [] if selected_company_id is None
        else [
            category
            for category in all_categories
            if category.company_id == selected_company_id
        ]
    )
except Exception as error:
    st.error("카테고리 데이터를 조회할 수 없습니다.")
    st.exception(error)
    st.stop()

category_name_by_id = {
    category.id: FAQService.normalize_category_name(category.name)
    for category in category_options
}
category_ids = [None] + [category.id for category in category_options]
selected_category_id = st.sidebar.selectbox(
    "카테고리",
    category_ids,
    format_func=lambda category_id: (
        "전체" if category_id is None else category_name_by_id[category_id]
    ),
)
keyword = st.sidebar.text_input("질문/답변 검색어").strip()

filter_state = (selected_company_id, selected_category_id, keyword)
if st.session_state.get("faq_filter_state") != filter_state:
    st.session_state.faq_page = 1
    st.session_state.faq_filter_state = filter_state

if "faq_page" not in st.session_state:
    st.session_state.faq_page = 1

try:
    faq_rows, total_count = load_faq_page(
        selected_company_id,
        selected_category_id,
        keyword,
        st.session_state.faq_page,
        PAGE_SIZE,
    )
except Exception as error:
    st.error("FAQ 데이터를 조회할 수 없습니다.")
    st.exception(error)
    st.stop()

total_pages = max((total_count - 1) // PAGE_SIZE + 1, 1)

if st.session_state.faq_page > total_pages:
    st.session_state.faq_page = total_pages
elif st.session_state.faq_page < 1:
    st.session_state.faq_page = 1

selected_page = st.session_state.faq_page
if selected_page != 1 and not faq_rows:
    faq_rows, total_count = load_faq_page(
        selected_company_id,
        selected_category_id,
        keyword,
        selected_page,
        PAGE_SIZE,
    )
    total_pages = max((total_count - 1) // PAGE_SIZE + 1, 1)

metric1, metric2, metric3 = st.columns(3)
metric1.metric("검색 결과", f"{total_count:,}건")
metric2.metric("회사 수", f"{len(company_options):,}개")
metric3.metric("카테고리 수", f"{len(category_options):,}개")

if not faq_rows:
    st.warning("검색 조건에 해당하는 FAQ가 없습니다.")
    st.stop()

st.divider()

start_index = (selected_page - 1) * PAGE_SIZE
end_index = start_index + PAGE_SIZE

st.caption(
    f"전체 {total_count:,}건 중 {start_index + 1:,}~{min(end_index, total_count):,}건 표시"
)

for faq in faq_rows:
    with st.expander(faq.question):
        st.markdown(faq.answer, unsafe_allow_html=True)

st.divider()
render_pagination(total_pages)
