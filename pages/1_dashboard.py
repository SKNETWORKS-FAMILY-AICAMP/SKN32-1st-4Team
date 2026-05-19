import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

import streamlit as st
import pydeck as pdk
import plotly.express as px
import pandas as pd

from service.vehicle_service import get_vehicle_data_from_db


# -----------------------------
# GeoJSON 설정
# -----------------------------
GEOJSON_PATH = Path("data/skorea-provinces-2018-geo.json")

DB_TO_GEO_NAME = {
    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",
    "경기": "경기도",
    "강원": "강원도",
    "충북": "충청북도",
    "충남": "충청남도",
    "전북": "전라북도",
    "전남": "전라남도",
    "경북": "경상북도",
    "경남": "경상남도",
    "제주": "제주특별자치도",
}


# -----------------------------
# GeoJSON 빌더
# -----------------------------
def build_vehicle_geojson(region_df, json_path=GEOJSON_PATH):

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)
    except FileNotFoundError:
        st.error(f"'{json_path}' 파일을 찾을 수 없습니다.")
        return None

    region_df = region_df.copy()
    region_df["geo_name"] = region_df["시도"].map(DB_TO_GEO_NAME)
    vehicle_dict = dict(zip(region_df["geo_name"], region_df["등록차량수"]))

    max_value = max(vehicle_dict.values()) if vehicle_dict else 1
    min_value = min(vehicle_dict.values()) if vehicle_dict else 0

    for feature in geojson["features"]:

        props         = feature["properties"]
        sido_name     = props.get("name", "")
        vehicle_count = vehicle_dict.get(sido_name, 0)

        if max_value > min_value:
            ratio = (vehicle_count - min_value) / (max_value - min_value)
        else:
            ratio = 0.5

        r = int(180 - ratio * 170)
        g = int(210 - ratio * 160)
        b = int(255 - ratio * 95)
        a = int(60  + ratio * 195)

        props["등록차량수"] = vehicle_count
        props["fill_color"] = [r, g, b, a]

    return geojson


# -----------------------------
# 데이터 로드 및 등록월 가공
# -----------------------------
df = get_vehicle_data_from_db()

# 등록월 → 연-월 만 표시 (2020-01-01 → 2020-01)
df["등록월"] = pd.to_datetime(df["등록월"]).dt.strftime("%Y-%m")

# -----------------------------
# 제목
# -----------------------------
st.title("시장 인사이트")

st.caption(
    "전국 자동차 등록 현황을 지역, 차량 종류, 월별 추이로 비교 조회합니다."
)

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.header("검색 조건")

month_options    = sorted(df["등록월"].unique().tolist(), reverse=True)
car_type_options = sorted(df["차량종류"].unique().tolist())
sido_options     = sorted(df["시도"].unique().tolist())

# 기본값 2026-04 설정
default_month = ["2026-04"] if "2026-04" in month_options else (month_options[:1] if month_options else [])

selected_months = st.sidebar.multiselect(
    "등록월",
    month_options,
    default=default_month,
    placeholder="Choose option",
)

selected_car_types = st.sidebar.multiselect(
    "차량종류",
    car_type_options,
    default=[],
    placeholder="Choose option",
)

selected_sidos = st.sidebar.multiselect(
    "비교할 시도",
    sido_options,
    default=[],
    placeholder="Choose option",
)

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

compare_level = st.sidebar.radio(
    "비교 기준",
    ["시도", "시군구"],
    horizontal=True,
)

# -----------------------------
# 데이터 필터링
# -----------------------------
national_df = df.copy()

if selected_months:
    national_df = national_df[national_df["등록월"].isin(selected_months)]

if selected_car_types:
    national_df = national_df[national_df["차량종류"].isin(selected_car_types)]

filtered_df = national_df.copy()

if selected_sidos:
    filtered_df = filtered_df[filtered_df["시도"].isin(selected_sidos)]

if selected_sigungus:
    filtered_df = filtered_df[filtered_df["시군구"].isin(selected_sigungus)]

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

    top_region   = "-"
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
    st.metric("총 등록 차량 수", f"{total_vehicle:,} 대")

with metric2:
    st.metric("등록 차량 최다 지역", top_region)

with metric3:
    st.metric("주요 차량 종류", top_car_type)

# -----------------------------
# 지역별 등록 차량 수
# -----------------------------
st.divider()

st.subheader("지역별 등록 차량 수")

map_col, type_col = st.columns([1.15, 1])

region_chart_df = (
    national_df.groupby("시도", as_index=False)["등록차량수"]
    .sum()
    .sort_values("등록차량수", ascending=False)
)

with map_col:

    st.markdown("#### 지역별 등록 차량 분포 지도")

    geojson_data = build_vehicle_geojson(region_chart_df)

    if national_df.empty or geojson_data is None:

        st.warning("지도에 표시할 지역 데이터가 없습니다.")

    else:

        geojson_layer = pdk.Layer(
            "GeoJsonLayer",
            data=geojson_data,
            opacity=0.8,
            stroked=True,
            filled=True,
            extruded=False,
            wireframe=True,
            get_fill_color="properties.fill_color",
            get_line_color=[255, 255, 255, 120],
            line_width_min_pixels=1,
            pickable=True,
        )

        deck = pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=36.2,
                longitude=127.8,
                zoom=6.2,
                pitch=0,
            ),
            layers=[geojson_layer],
            tooltip={
                "html": "<b>{name}</b><br/>등록 차량 수: {등록차량수} 대",
                "style": {"backgroundColor": "#111827", "color": "white"},
            },
            map_style="light",
        )

        st.pydeck_chart(deck, use_container_width=True, height=430)

        st.markdown("""
        <div style='display:flex; align-items:center; gap:8px; margin-top:6px; font-size:12px; color:#6b7280;'>
            <span>낮음</span>
            <div style='width:150px; height:12px; border-radius:6px;
                background:linear-gradient(to right, #b4d2ff, #0a3296);'></div>
            <span>높음</span>
        </div>
        """, unsafe_allow_html=True)

with type_col:

    st.markdown("#### 차량 종류별 등록 현황")

    car_chart_df = (
        filtered_df.groupby("차량종류", as_index=False)["등록차량수"]
        .sum()
        .sort_values("등록차량수", ascending=False)
        .reset_index(drop=True)
    )

    if car_chart_df.empty:

        st.warning("표시할 차량 종류별 데이터가 없습니다.")

    else:

        blue_scale = [
            "#0B3D91",
            "#1D4ED8",
            "#2563EB",
            "#3B82F6",
            "#60A5FA",
            "#93C5FD",
            "#BFDBFE",
            "#DBEAFE",
        ]

        car_chart_df["막대색상"] = [
            blue_scale[min(idx, len(blue_scale) - 1)]
            for idx in range(len(car_chart_df))
        ]

        fig_car = px.bar(
            car_chart_df,
            x="차량종류",
            y="등록차량수",
            text="등록차량수",
            title="차량 종류별 등록 현황",
            color="막대색상",
            color_discrete_map={
                color: color
                for color in car_chart_df["막대색상"].unique()
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
            margin=dict(l=0, r=0, t=45, b=0),
            showlegend=False,
        )

        st.plotly_chart(fig_car, use_container_width=True)

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
        # x축 날짜 포맷 연-월만 표시
        xaxis=dict(
            type="category",
            tickformat="%Y-%m",
        ),
    )

    st.plotly_chart(fig_month, use_container_width=True)

# -----------------------------
# 상세 데이터 보기
# -----------------------------
st.divider()

with st.expander("상세 데이터 보기", expanded=False):

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
