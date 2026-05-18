import sys
import os

# 프로젝트 루트 경로를 시스템 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pydeck as pdk
import plotly.express as px

from service.vehicle_service import get_vehicle_data_from_db


REGION_COORDS = {
    "서울특별시": {"lat": 37.5665, "lon": 126.9780},
    "경기도": {"lat": 37.4138, "lon": 127.5183},
    "부산광역시": {"lat": 35.1796, "lon": 129.0756},
    "대구광역시": {"lat": 35.8714, "lon": 128.6014},
    "인천광역시": {"lat": 37.4563, "lon": 126.7052},
    "강원특별자치도": {"lat": 37.8228, "lon": 128.1555},
    "경상남도": {"lat": 35.4606, "lon": 128.2132},
}


def add_map_columns(region_df):

    map_df = region_df.copy()

    map_df["lat"] = map_df["시도"].map(
        lambda sido: REGION_COORDS.get(sido, {}).get("lat")
    )

    map_df["lon"] = map_df["시도"].map(
        lambda sido: REGION_COORDS.get(sido, {}).get("lon")
    )

    map_df = map_df.dropna(subset=["lat", "lon"])

    if map_df.empty:
        return map_df

    max_value = max(map_df["등록차량수"].max(), 1)

    map_df["radius"] = map_df["등록차량수"].map(
        lambda value: 18000 + int((value / max_value) * 52000)
    )

    map_df["fill_color"] = map_df["등록차량수"].map(
        lambda value: [29, 78, 216, 70 + int((value / max_value) * 140)]
    )

    map_df["label"] = map_df.apply(
        lambda row: f"{row['시도']}\n{row['등록차량수']:,}대",
        axis=1,
    )

    return map_df


# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="자동차 등록 현황",
    page_icon="car",
    layout="wide",
)

# -----------------------------
# 데이터 로드
# -----------------------------
df = get_vehicle_data_from_db()

# -----------------------------
# 제목
# -----------------------------
st.title("전국 자동차 등록 현황")

st.caption(
    "지역별 자동차 등록 대수와 월별 등록 추이를 비교 조회할 수 있습니다."
)

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.header("검색 조건")

month_options = sorted(
    df["등록월"].unique().tolist(),
    reverse=True
)

car_type_options = sorted(
    df["차량종류"].unique().tolist()
)

sido_options = sorted(
    df["시도"].unique().tolist()
)

# -----------------------------
# 등록월 선택
# -----------------------------
selected_months = st.sidebar.multiselect(
    "등록월",
    month_options,
    default=[],
    placeholder="Choose option",
)

# -----------------------------
# 차량종류 선택
# -----------------------------
selected_car_types = st.sidebar.multiselect(
    "차량종류",
    car_type_options,
    default=[],
    placeholder="Choose option",
)

# -----------------------------
# 비교할 시도 선택
# 여러 개 선택 가능
# -----------------------------
selected_sidos = st.sidebar.multiselect(
    "비교할 시도",
    sido_options,
    default=[],
    placeholder="Choose option",
)

# -----------------------------
# 시도별 시군구 선택
# -----------------------------
selected_sigungus = []

for sido in selected_sidos:

    sigungu_options = sorted(
        df[df["시도"] == sido]["시군구"]
        .dropna()
        .unique()
        .tolist()
    )

    selected = st.sidebar.multiselect(
        f"{sido} 시군구 선택",
        sigungu_options,
        default=[],
        placeholder=f"{sido} 시군구 선택",
    )

    selected_sigungus.extend(selected)

# -----------------------------
# 비교 기준
# -----------------------------
compare_level = st.sidebar.radio(
    "비교 기준",
    ["시도", "시군구"],
    horizontal=True,
)

# -----------------------------
# 데이터 필터링
# -----------------------------
filtered_df = df.copy()

if selected_months:

    filtered_df = filtered_df[
        filtered_df["등록월"].isin(selected_months)
    ]

if selected_car_types:

    filtered_df = filtered_df[
        filtered_df["차량종류"].isin(selected_car_types)
    ]

if selected_sidos:

    filtered_df = filtered_df[
        filtered_df["시도"].isin(selected_sidos)
    ]

if selected_sigungus:

    filtered_df = filtered_df[
        filtered_df["시군구"].isin(selected_sigungus)
    ]

# -----------------------------
# 조회 요약
# -----------------------------
st.divider()

st.subheader("조회 요약")

total_vehicle = (
    int(filtered_df["등록차량수"].sum())
    if not filtered_df.empty
    else 0
)

if filtered_df.empty:

    top_region = "-"
    top_car_type = "-"

else:

    top_region = (
        filtered_df.groupby("시도")["등록차량수"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    top_car_type = (
        filtered_df.groupby("차량종류")["등록차량수"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

metric1, metric2, metric3 = st.columns(3)

with metric1:

    st.metric(
        "총 등록 차량 수",
        f"{total_vehicle:,} 대"
    )

with metric2:

    st.metric(
        "등록 차량 최다 지역",
        top_region
    )

with metric3:

    st.metric(
        "주요 차량 종류",
        top_car_type
    )

# -----------------------------
# 지역별 등록 차량 수
# -----------------------------
st.divider()

st.subheader("지역별 등록 차량 수")

map_col, type_col = st.columns([1.15, 1])

region_chart_df = (
    filtered_df.groupby("시도", as_index=False)["등록차량수"]
    .sum()
    .sort_values("등록차량수", ascending=False)
)

# -----------------------------
# 지도
# -----------------------------
with map_col:

    st.markdown("#### 지역별 등록 차량 수 지도")

    map_df = add_map_columns(region_chart_df)

    if map_df.empty:

        st.warning("지도에 표시할 지역 데이터가 없습니다.")

    else:

        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_weight="등록차량수",
            radiusPixels=90,
            intensity=1.3,
            threshold=0.05,
        )

        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_radius="radius",
            get_fill_color="fill_color",
            get_line_color=[30, 64, 175, 220],
            line_width_min_pixels=1,
            pickable=True,
        )

        text_layer = pdk.Layer(
            "TextLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_text="label",
            get_size=13,
            get_color=[17, 24, 39, 230],
            get_alignment_baseline="'center'",
            get_text_anchor="'middle'",
        )

        deck = pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=36.35,
                longitude=127.8,
                zoom=6,
                pitch=0,
            ),
            layers=[
                heatmap_layer,
                scatter_layer,
                text_layer,
            ],
            tooltip={
                "html": "<b>{시도}</b><br/>등록 차량 수: {등록차량수}대",
                "style": {
                    "backgroundColor": "#111827",
                    "color": "white",
                },
            },
            map_style="light",
        )

        st.pydeck_chart(
            deck,
            use_container_width=True,
            height=430,
        )

# -----------------------------
# 차량 종류별 그래프
# -----------------------------
with type_col:

    st.markdown("#### 차량 종류별 등록 현황")

    car_chart_df = (
        filtered_df.groupby(
            "차량종류",
            as_index=False
        )["등록차량수"]
        .sum()
        .sort_values(
            "등록차량수",
            ascending=False
        )
        .reset_index(drop=True)
    )

    if car_chart_df.empty:

        st.warning("표시할 차량 종류별 데이터가 없습니다.")

    else:

        rank_colors = []

        for idx in range(len(car_chart_df)):

            if idx == 0:
                rank_colors.append("빨강")

            elif idx == 1:
                rank_colors.append("초록")

            elif idx == 2:
                rank_colors.append("노랑")

            else:
                rank_colors.append("파랑")

        car_chart_df["색상"] = rank_colors

        fig_car = px.bar(
            car_chart_df,
            x="차량종류",
            y="등록차량수",
            text="등록차량수",
            title="차량 종류별 등록 현황",
            color="색상",
            color_discrete_map={
                "빨강": "#ef4444",
                "초록": "#22c55e",
                "노랑": "#facc15",
                "파랑": "#3b82f6",
            },
        )

        fig_car.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
        )

        fig_car.update_layout(
            yaxis_title="등록 차량 수",
            xaxis_title="",
            height=430,
            margin=dict(
                l=0,
                r=0,
                t=45,
                b=0,
            ),
            showlegend=False,
        )

        st.plotly_chart(
            fig_car,
            use_container_width=True,
        )

# -----------------------------
# 월별 등록 추이 비교
# -----------------------------
st.divider()

st.subheader("월별 등록 추이 비교")

comparison_column = (
    "시군구"
    if compare_level == "시군구"
    else "시도"
)

monthly_compare_df = (
    filtered_df.groupby(
        ["등록월", comparison_column],
        as_index=False
    )["등록차량수"]
    .sum()
    .sort_values("등록월")
)

if monthly_compare_df.empty:

    st.warning("표시할 월별 데이터가 없습니다.")

else:

    fig_month = px.line(
        monthly_compare_df,
        x="등록월",
        y="등록차량수",
        color=comparison_column,
        markers=True,
        title=f"월별 등록 차량 수 비교 - {comparison_column}",
    )

    fig_month.update_layout(
        yaxis_title="등록 차량 수",
        xaxis_title="등록월",
        legend_title_text=comparison_column,
    )

    st.plotly_chart(
        fig_month,
        use_container_width=True,
    )

# -----------------------------
# 상세 데이터 보기
# -----------------------------
st.divider()

with st.expander(
    "상세 데이터 보기",
    expanded=False
):

    st.caption(
        "사이드바에서 선택한 등록월, 차량종류, 지역 조건에 포함된 원본 샘플 데이터입니다."
    )

    st.write(f"총 **{len(filtered_df)}건**")

    if filtered_df.empty:

        st.info("선택 조건에 맞는 데이터가 없습니다.")

    else:

        display_df = filtered_df.copy()

        display_df["등록차량수"] = display_df["등록차량수"].map(
            lambda value: f"{value:,}"
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )