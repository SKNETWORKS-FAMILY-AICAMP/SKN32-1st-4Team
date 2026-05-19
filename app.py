import streamlit as st


st.set_page_config(
    page_title="K-Car Navigator",
    page_icon="car",
    layout="wide",
)


def render_home():
    st.title("K-Car Navigator")
    st.subheader("자동차 등록 데이터와 브랜드 FAQ를 한곳에서 탐색합니다")

    st.markdown(
        """
### 서비스 안내

**K-Car Navigator**는 전국 자동차 등록 현황과 자동차 기업 FAQ 데이터를
빠르게 조회하고 비교할 수 있는 데이터 탐색 서비스입니다.

#### 주요 기능
- **시장 인사이트**
  - 지역별 자동차 등록 대수 조회
  - 차량 종류별 통계 확인
  - 선택 지역의 월별 등록 추이 비교

- **FAQ 센터**
  - 현대자동차 / 기아 자동차 /BMW FAQ 조회
  - 회사별, 카테고리별 검색
  - 질문 및 답변 키워드 검색
"""
    )

    st.info("왼쪽 사이드바에서 원하는 메뉴를 선택해 주세요.")


pages = [
    st.Page(render_home, title="K-Car Navigator", icon=":material/home:"),
    st.Page("pages/1_dashboard.py", title="시장 인사이트", icon=":material/analytics:"),
    st.Page("pages/2_faq.py", title="FAQ 센터", icon=":material/help:"),
]

navigation = st.navigation(pages)
navigation.run()
