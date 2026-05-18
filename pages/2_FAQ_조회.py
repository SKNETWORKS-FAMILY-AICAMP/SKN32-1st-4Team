import html
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(page_title="FAQ 조회", page_icon="?", layout="wide")

DATA_DIR = Path(__file__).resolve().parents[1] / "data_backup"
FAQ_FILES = [
    ("현대자동차", DATA_DIR / "HYUNDAI_1_faq.json"),
    ("기아자동차", DATA_DIR / "KIA_2_faq.json"),
    ("BMW", DATA_DIR / "BMW_3_faq.json"),
]

PAGE_SIZE = 20


def normalize_category(category):
    category = str(category or "").strip()
    if not category or category.casefold() == "web":
        return "기타"
    return category


def html_to_text(value):
    text = html.unescape(str(value or ""))
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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


@st.cache_data
def load_faq_data():
    rows = []

    for company, path in FAQ_FILES:
        with path.open("r", encoding="utf-8") as file:
            items = json.load(file)

        for item in items:
            answer = item.get("answer", "")
            rows.append(
                {
                    "company": company,
                    "company_id": item.get("company_id"),
                    "category": normalize_category(item.get("category_name")),
                    "display_order": item.get("display_order", 999),
                    "question": str(item.get("question", "")).strip(),
                    "answer": answer,
                    "answer_text": html_to_text(answer),
                }
            )

    return pd.DataFrame(rows).sort_values(
        ["company_id", "display_order", "category", "question"],
        kind="stable",
    )


st.title("FAQ 조회")

try:
    df = load_faq_data()
except FileNotFoundError as error:
    st.error(f"FAQ 데이터 파일을 찾을 수 없습니다: {error.filename}")
    st.stop()

st.sidebar.header("검색 조건")

companies = ["전체"] + [company for company, _ in FAQ_FILES]
selected_company = st.sidebar.selectbox("회사", companies)

category_source = df
if selected_company != "전체":
    category_source = category_source[category_source["company"] == selected_company]

category_options = (
    category_source[["category", "display_order"]]
    .drop_duplicates()
    .sort_values(["display_order", "category"], kind="stable")["category"]
    .tolist()
)
selected_category = st.sidebar.selectbox("카테고리", ["전체"] + category_options)
keyword = st.sidebar.text_input("질문/답변 검색어").strip()

filter_state = (selected_company, selected_category, keyword)
if st.session_state.get("faq_filter_state") != filter_state:
    st.session_state.faq_page = 1
    st.session_state.faq_filter_state = filter_state

filtered = df.copy()

if selected_company != "전체":
    filtered = filtered[filtered["company"] == selected_company]

if selected_category != "전체":
    filtered = filtered[filtered["category"] == selected_category]

if keyword:
    keyword_mask = (
        filtered["question"].str.contains(keyword, case=False, na=False, regex=False)
        | filtered["answer_text"].str.contains(
            keyword,
            case=False,
            na=False,
            regex=False,
        )
        | filtered["category"].str.contains(keyword, case=False, na=False, regex=False)
    )
    filtered = filtered[keyword_mask]

metric1, metric2, metric3 = st.columns(3)
metric1.metric("검색 결과", f"{len(filtered):,}건")
metric2.metric("회사 수", f"{filtered['company'].nunique():,}개")
metric3.metric("카테고리 수", f"{filtered['category'].nunique():,}개")

if filtered.empty:
    st.warning("검색 조건에 해당하는 FAQ가 없습니다.")
    st.stop()

st.divider()

total_count = len(filtered)
total_pages = max((total_count - 1) // PAGE_SIZE + 1, 1)

if "faq_page" not in st.session_state:
    st.session_state.faq_page = 1

if st.session_state.faq_page > total_pages:
    st.session_state.faq_page = total_pages
elif st.session_state.faq_page < 1:
    st.session_state.faq_page = 1

selected_page = st.session_state.faq_page

start_index = (selected_page - 1) * PAGE_SIZE
end_index = start_index + PAGE_SIZE
page_df = filtered.iloc[start_index:end_index]

st.caption(
    f"전체 {total_count:,}건 중 {start_index + 1:,}~{min(end_index, total_count):,}건 표시"
)

for row in page_df.itertuples(index=False):
    with st.expander(f"[{row.company} / {row.category}] {row.question}"):
        st.markdown(row.answer, unsafe_allow_html=True)

st.divider()
render_pagination(total_pages)
