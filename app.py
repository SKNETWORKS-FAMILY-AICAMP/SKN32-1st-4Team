import streamlit as st


st.set_page_config(
    page_title="K-Car Navigator",
    page_icon="car",
    layout="wide",
)

st.title("K-Car Navigator")
st.subheader("전국 자동차 등록 현황 및 자동차 기업 FAQ 조회 서비스")

st.markdown(
    """
### 프로젝트 소개

**K-Car Navigator**는 전국 자동차 등록 현황 데이터와 자동차 기업 FAQ 데이터를
조회할 수 있는 간단한 Streamlit 서비스입니다.

왼쪽 사이드바에서 원하는 기능을 선택하세요.

#### 제공 기능
- **자동차 등록 현황**
  - 지역별 자동차 등록 대수 조회
  - 차량 종류별 통계 확인
  - 선택 지역의 월별 등록 추이 확인

- **FAQ 조회**
  - 현대자동차 / BMW FAQ 조회
  - 회사별, 카테고리별 검색
  - 질문 및 답변 키워드 검색
"""
)

st.info("왼쪽 사이드바에서 원하는 페이지를 선택해 주세요.")
