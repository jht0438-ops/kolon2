import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="KOLON Global Financial Insight",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# 기본 스타일
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.8rem; padding-bottom: 2.5rem;}
h1, h2, h3 {letter-spacing: -0.03em;}
.kolon-card {
    border: 1px solid #e8e8e8;
    border-radius: 16px;
    padding: 18px 20px;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.kolon-note {
    border-left: 4px solid #2458d3;
    background: #f6f8ff;
    padding: 14px 16px;
    border-radius: 8px;
    margin: 8px 0 14px 0;
}
.small {color:#666; font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 공시자료 기반 데이터
# 단위: 억원 (별도 표시가 없는 경우)
# -----------------------------

# 1) 2025 판매경로별 매출
# 원자료 단위: 백만원
portfolio = pd.DataFrame({
    "사업부문": ["건설", "상사", "레저", "AM"],
    "매출액_억원": [23079.78, 3025.76, 760.35, 45.86],
    "비중": [85.8, 11.3, 2.8, 0.2]
})

# 2) 건설 신규수주 및 수주잔고
# 2023 3.1조, 2024 4.2조는 사업보고서 기재 수치.
# 2025는 "약 3조원을 돌파"라는 공시 표현이므로 정확한 막대값으로 단정하지 않고 텍스트로만 표시.
orders = pd.DataFrame({
    "연도": ["2023", "2024"],
    "신규수주_조원": [3.1, 4.2]
})
backlog_2025 = 11.8  # 조원
construction_sales_2025 = portfolio.loc[portfolio["사업부문"]=="건설", "매출액_억원"].iloc[0]
backlog_years = backlog_2025 * 10000 / construction_sales_2025

# 3) 건설계약 매출 → 청구 → 회수 분석
# (a) '계약금액이 전기 매출액의 5% 이상인 주요 계약' 표 합계
cash_conversion = pd.DataFrame({
    "연도": ["2023", "2024", "2025"],
    "미청구공사_억원": [789.62, 865.60, 1235.23],
    "공사미수금_억원": [964.92, 1547.41, 1536.11]
})
cash_conversion["합계_억원"] = cash_conversion["미청구공사_억원"] + cash_conversion["공사미수금_억원"]
cash_conversion["전년대비_증감률"] = cash_conversion["합계_억원"].pct_change() * 100

# (b) 전체 진행 중 건설계약의 미청구공사(공사미수금, 미청구분)
# 2025 사업보고서 건설계약 주석 기준
whole_unbilled = pd.DataFrame({
    "구분": ["국내토목", "국내건축", "국내플랜트", "국내주택", "국내환경", "해외도급"],
    "2024_억원": [926.07, 483.32, 78.58, 1041.86, 65.12, 399.37],
    "2025_억원": [725.35, 301.85, 161.52, 1477.48, 87.01, 229.66]
})
whole_unbilled["증감_억원"] = whole_unbilled["2025_억원"] - whole_unbilled["2024_억원"]
whole_unbilled_total_2024 = whole_unbilled["2024_억원"].sum()
whole_unbilled_total_2025 = whole_unbilled["2025_억원"].sum()

# (c) 주요계약 중 2024→2025 미청구공사 변동을 크게 만든 프로젝트
# 사업보고서의 전기/당기 주요계약 표를 동일 프로젝트 기준으로 매칭한 값
project_unbilled_drivers = pd.DataFrame({
    "프로젝트": [
        "삼성전자 평택 사무6동 신축공사",
        "대한항공 엔진정비공장 증축공사",
        "부산 기장 물류센터 신축공사",
        "부산 엄궁1구역 주택재개발정비사업",
        "양평 덕평지구 지역주택조합",
        "대전 선화동 주상복합",
        "대전 대성동 공동주택",
        "세운4구역 도시환경정비사업",
        "대전 봉명동 주상복합",
        "대전 선화동2 주상복합"
    ],
    "증감_억원": [239.7, 161.5, 145.1, 66.9, 58.1, -203.0, -141.8, -62.8, -49.4, -45.4]
})

# (d) 계약금액·총원가 추정 변경이 미청구공사(초과청구공사)에 미친 영향
estimate_change_2025 = pd.DataFrame({
    "구분": ["국내토목", "국내건축", "국내플랜트", "국내주택", "국내환경", "해외도급"],
    "추정변경_영향_억원": [-319.62, -30.07, 117.59, 110.05, -46.53, 25.53]
})

# 4) 연결 영업현금흐름 및 운전자본 변동
# 2025 사업보고서 연결 현금흐름표 기준 (단위: 억원)
operating_cf = pd.DataFrame({
    "연도": ["2023", "2024", "2025"],
    "영업활동현금흐름_억원": [-1483.60, -2132.67, 723.56],
    "영업에서창출된현금_억원": [-1115.50, -1427.98, 1232.66],
    "운전자본변동_억원": [-1689.97, -1570.62, 311.34],
    "매출채권증감_현금효과_억원": [-3235.72, -1096.81, -755.90]
})

# 2025 영업현금흐름 개선 원인: 2024 대비 운전자본 항목별 현금효과 변화
wc_bridge = pd.DataFrame({
    "항목": [
        "매입채무", "기타유동부채", "기타유동자산", "기타비유동자산",
        "매출채권", "기타유동채권", "재고자산", "기타유동채무",
        "충당부채", "기타비유동채권"
    ],
    "2024_현금효과_억원": [
        -2193.25, 1668.30, -455.24, -39.26, -1096.81,
        264.90, 329.55, 316.61, -33.56, -70.13
    ],
    "2025_현금효과_억원": [
        562.65, 10.90, 217.24, -452.91, -755.90,
        -56.94, 32.26, 53.68, 136.00, -0.13
    ]
})
wc_bridge["전년대비_개선효과_억원"] = (
    wc_bridge["2025_현금효과_억원"] - wc_bridge["2024_현금효과_억원"]
)

# 2025 주요 프로젝트 일부
projects_2025 = pd.DataFrame({
    "프로젝트": [
        "수원 권선6구역 재건축",
        "강북구 번동 1~5구역 가로주택정비사업",
        "부산 온천장 지역주택조합 주상복합",
        "청주동남 A2 민간참여 공공주택사업",
        "안양 냉천지구 주거환경개선사업",
        "고속국도 제30호 대산-당진 제1공구",
        "전주 삼천주공 3단지 재건축"
    ],
    "수주총액_억원": [2154.18, 3881.05, 1582.64, 1240.56, 1227.22, 1243.80, 1619.92],
    "진행률_%": [59.47, 2.60, 4.62, 10.51, 100.00, 3.80, 0.30],
    "미청구공사_억원": [0.00, 33.76, 14.56, 34.11, 3.31, 2.34, 4.50],
    "공사미수금_억원": [0.00, 0.00, 0.00, 0.00, 0.12, 4.47, 0.00]
})

# -----------------------------
# 공통 상단
# -----------------------------
st.title("KOLON Global Financial Insight")
st.caption("코오롱글로벌의 사업구조 → 건설 수주 → 현금전환 흐름을 연결해 보는 재무분석 대시보드")

m1, m2, m3, m4 = st.columns(4)
m1.metric("2025 총매출", "2조 6,912억원")
m2.metric("건설 매출 비중", "85.8%")
m3.metric("2025 건설 수주잔고", "약 11.8조원")
m4.metric("수주잔고 ÷ 건설매출", f"약 {backlog_years:.1f}배")

st.markdown("""
<div class="kolon-note">
<b>분석 방향</b><br>
① 코오롱글로벌은 어디서 매출을 만드는가 → ② 핵심 건설사업의 미래 매출 기반은 어떠한가
→ ③ 주요계약의 미청구 증가를 프로젝트와 전체 건설계약 관점에서 검증하는가
→ ④ 실제 영업현금흐름은 어떻게 변했고, 2025년 개선을 만든 운전자본 요인은 무엇인가
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "① 사업 포트폴리오",
    "② 수주 → 매출",
    "③ 매출 → 청구 → 회수",
    "④ 영업현금흐름 개선 분석"
])

# -----------------------------
# TAB 1. 사업 포트폴리오
# -----------------------------
with tab1:
    st.subheader("① 사업 포트폴리오 분석")
    st.write("2025년 판매경로별 매출액을 기준으로 코오롱글로벌의 사업구조를 확인합니다.")

    c1, c2 = st.columns([1, 1.15])

    with c1:
        fig = px.pie(
            portfolio,
            names="사업부문",
            values="매출액_억원",
            hole=0.58
        )
        fig.update_traces(
            texttemplate="%{label}<br>%{percent:.1%}",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f}억원<extra></extra>"
        )
        fig.update_layout(
            title="2025 사업부문별 매출 구성",
            legend_title_text="",
            margin=dict(t=60, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        df_show = portfolio.copy()
        df_show["매출액"] = df_show["매출액_억원"].map(lambda x: f"{x:,.0f}억원")
        df_show["비중"] = df_show["비중"].map(lambda x: f"{x:.1f}%")
        st.dataframe(
            df_show[["사업부문", "매출액", "비중"]],
            hide_index=True,
            use_container_width=True
        )

        st.markdown("""
        <div class="kolon-card">
        <b>해석</b><br><br>
        2025년 매출의 약 <b>85.8%</b>가 건설부문에서 발생합니다.
        따라서 코오롱글로벌 전체 재무를 이해할 때 건설사업의
        수주, 매출 인식, 회수 관련 계정을 우선적으로 살펴볼 필요가 있습니다.<br><br>
        상사는 약 11.3%, 레저는 약 2.8%, AM은 약 0.2%를 차지합니다.
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "레저부문에는 호텔·골프/리조트·스포렉스가 포함되고, "
        "AM은 오피스·사옥·지식산업센터 등 자산관리 관련 사업입니다."
    )

# -----------------------------
# TAB 2. 수주 → 매출
# -----------------------------
with tab2:
    st.subheader("② 건설 수주 → 매출 분석")
    st.write("건설부문의 신규수주와 수주잔고를 현재 매출 규모와 함께 봅니다.")

    a, b, c = st.columns(3)
    a.metric("2023 신규수주", "3.1조원")
    b.metric("2024 신규수주", "4.2조원")
    c.metric("2025 신규수주", "약 3조원 돌파")

    fig2 = px.bar(
        orders,
        x="연도",
        y="신규수주_조원",
        text="신규수주_조원",
        labels={"신규수주_조원": "신규수주(조원)", "연도": ""}
    )
    fig2.update_traces(texttemplate="%{text:.1f}조", textposition="outside")
    fig2.update_layout(
        title="공시에서 확인되는 신규수주 추이",
        yaxis_range=[0, max(orders["신규수주_조원"]) * 1.25]
    )
    st.plotly_chart(fig2, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""
        <div class="kolon-card">
        <b>2025년 말 수주잔고</b><br>
        <span style="font-size:2rem;font-weight:700;">약 11.8조원</span><br><br>
        회사는 2015년 이후 매년 2조원 이상의 신규수주를 기록해 왔으며,
        2025년 말 기준 약 11.8조원의 수주잔고를 보유하고 있다고 공시했습니다.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kolon-card">
        <b>수주잔고 / 2025 건설매출</b><br>
        <span style="font-size:2rem;font-weight:700;">약 {backlog_years:.1f}배</span><br><br>
        단순 환산 시 현재 1년 건설매출의 약 {backlog_years:.1f}배 규모입니다.
        다만 수주잔고가 그대로 동일 기간 내 매출로 인식되는 것은 아니므로,
        <b>미래 매출 기반의 참고지표</b>로 해석해야 합니다.
        </div>
        """, unsafe_allow_html=True)

    st.warning(
        "2025년 신규수주는 사업보고서에서 '약 3조원을 돌파'라고 표현되어 있어 "
        "정확한 수치로 임의 환산하지 않았습니다."
    )

# -----------------------------
# TAB 3. 현금전환 분석
# -----------------------------
with tab3:
    st.subheader("③ 건설계약 매출 → 청구 → 회수 분석")
    st.write("미청구공사와 공사미수금을 단순 잔액으로 보지 않고, 매출이 현금으로 전환되는 과정의 어느 단계에 금액이 쌓이는지 확인합니다.")

    st.markdown("""
    <div class="kolon-note">
    <b>왜 이 두 계정을 보는가?</b><br><br>
    건설사업은 <b>공사진행 → 매출 인식 → 청구 → 현금 회수</b>의 과정을 거칩니다.<br>
    • <b>미청구공사</b>: 공사진행에 따라 매출은 인식됐지만 아직 청구 전 단계에 있는 금액<br>
    • <b>공사미수금</b>: 청구는 완료됐지만 아직 현금으로 회수되지 않은 금액<br><br>
    따라서 두 계정을 함께 보면 현금전환 과정에서 <b>청구 전 단계와 회수 전 단계 중 어디에 잔액이 쌓이는지</b> 확인할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 1. 주요 건설계약: 2025년에는 어디에서 잔액이 늘었나?")
    st.caption("아래 금액은 회사 전체가 아니라, 사업보고서의 '계약금액이 전기 매출액의 5% 이상인 주요 건설계약' 표의 합계입니다.")

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=cash_conversion["연도"], y=cash_conversion["미청구공사_억원"], name="미청구공사"))
    fig3.add_trace(go.Bar(x=cash_conversion["연도"], y=cash_conversion["공사미수금_억원"], name="공사미수금"))
    fig3.update_layout(barmode="group", title="주요 건설계약 기준 미청구공사·공사미수금", yaxis_title="억원", legend_title_text="")
    st.plotly_chart(fig3, use_container_width=True)

    latest = cash_conversion.iloc[-1]
    prev = cash_conversion.iloc[-2]
    col1, col2, col3 = st.columns(3)
    col1.metric("2025 주요계약 미청구공사", f"{latest['미청구공사_억원']:,.0f}억원", f"{(latest['미청구공사_억원']/prev['미청구공사_억원']-1)*100:.1f}%")
    col2.metric("2025 주요계약 공사미수금", f"{latest['공사미수금_억원']:,.0f}억원", f"{(latest['공사미수금_억원']/prev['공사미수금_억원']-1)*100:.1f}%")
    col3.metric("2025 두 계정 합계", f"{latest['합계_억원']:,.0f}억원", f"{latest['전년대비_증감률']:.1f}%")

    st.markdown("""
    <div class="kolon-card">
    <b>1차 진단</b><br><br>
    2025년 주요계약 공사미수금은 전년 대비 <b>0.7% 감소</b>해 청구 후 미회수 잔액은 추가로 확대되지 않았습니다.
    반면 미청구공사는 <b>42.7% 증가</b>했습니다. 즉 주요계약에서는 2025년 잔액 증가가 <b>회수 전 단계보다 매출 인식 후 청구 전 단계</b>에 집중됐습니다.
    다만 이것만으로 회사 전체 현금전환이 악화됐다고 판단할 수는 없습니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 2. +369.6억원의 미청구공사 증가: 어떤 프로젝트가 만들었나?")
    drivers = project_unbilled_drivers.sort_values("증감_억원")
    fig_driver = px.bar(
        drivers, x="증감_억원", y="프로젝트", orientation="h", text="증감_억원",
        labels={"증감_억원":"2024 → 2025 미청구공사 증감(억원)", "프로젝트":""},
        title="주요 프로젝트별 미청구공사 증감 기여"
    )
    fig_driver.update_traces(texttemplate="%{text:+.1f}", textposition="outside")
    fig_driver.add_vline(x=0, line_width=1, line_dash="dash")
    fig_driver.update_layout(height=520)
    st.plotly_chart(fig_driver, use_container_width=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("""
        <div class="kolon-card">
        <b>증가 측 주요 요인</b><br><br>
        삼성전자 평택 사무6동 신축공사 <b>+239.7억원</b>, 대한항공 엔진정비공장 증축공사 <b>+161.5억원</b>,
        부산 기장 물류센터 신축공사 <b>+145.1억원</b> 등이 주요 증가 요인으로 확인됩니다.
        </div>
        """, unsafe_allow_html=True)
    with d2:
        st.markdown("""
        <div class="kolon-card">
        <b>감소 측 주요 요인</b><br><br>
        대전 선화동 주상복합 <b>-203.0억원</b>, 대전 대성동 공동주택 <b>-141.8억원</b> 등에서는 미청구공사가 감소했습니다.
        즉 전체 증가는 모든 현장의 일괄적인 악화가 아니라 <b>프로젝트별 증감이 상쇄된 결과</b>입니다.
        </div>
        """, unsafe_allow_html=True)

    st.caption("프로젝트별 증감은 사업보고서의 2024·2025 주요계약 표를 동일 프로젝트 기준으로 매칭한 분석입니다. 공개자료만으로 각 현장의 세부 청구조건이나 발주처별 청구 시점까지는 확인할 수 없습니다.")

    st.markdown("#### 3. 회사 전체 건설계약으로 넓혀 보면?")
    whole_compare = pd.DataFrame({
        "연도": ["2024", "2025"],
        "전체 미청구공사_억원": [whole_unbilled_total_2024, whole_unbilled_total_2025]
    })
    c1, c2, c3 = st.columns(3)
    c1.metric("2024 전체 미청구공사", f"{whole_unbilled_total_2024:,.0f}억원")
    c2.metric("2025 전체 미청구공사", f"{whole_unbilled_total_2025:,.0f}억원", f"{whole_unbilled_total_2025-whole_unbilled_total_2024:+,.0f}억원")
    c3.metric("주요계약 미청구공사 증감", "+370억원", "전년 대비 +42.7%")

    fig_whole = go.Figure()
    fig_whole.add_trace(go.Bar(name="2024", x=whole_unbilled["구분"], y=whole_unbilled["2024_억원"]))
    fig_whole.add_trace(go.Bar(name="2025", x=whole_unbilled["구분"], y=whole_unbilled["2025_억원"]))
    fig_whole.update_layout(barmode="group", title="전체 진행 중 건설계약: 부문별 미청구공사", yaxis_title="억원", legend_title_text="")
    st.plotly_chart(fig_whole, use_container_width=True)

    st.markdown("""
    <div class="kolon-note">
    <b>범위를 넓히면 결론이 달라집니다.</b><br><br>
    주요 대형계약만 보면 미청구공사가 <b>865.6억원 → 1,235.2억원(+42.7%)</b>으로 크게 증가했습니다.
    그러나 전체 진행 중 건설계약의 미청구공사는 <b>2,994.3억원 → 2,982.9억원</b>으로 약 <b>11.5억원 감소</b>해 사실상 보합입니다.<br><br>
    즉 2025년 미청구공사 증가는 회사 전체에 광범위하게 나타난 현상이라기보다, <b>일부 주요 대형 프로젝트에서 두드러진 현상</b>으로 보는 것이 더 적절합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 4. 전체 미청구공사는 왜 보합이었나?")
    change_sorted = whole_unbilled.sort_values("증감_억원")
    fig_seg = px.bar(change_sorted, x="증감_억원", y="구분", orientation="h", text="증감_억원",
                     labels={"증감_억원":"2024 → 2025 증감(억원)", "구분":""},
                     title="부문별 전체 미청구공사 증감")
    fig_seg.update_traces(texttemplate="%{text:+.1f}", textposition="outside")
    fig_seg.add_vline(x=0, line_width=1, line_dash="dash")
    st.plotly_chart(fig_seg, use_container_width=True)

    st.write("국내주택은 약 **+435.6억원** 증가했지만 국내토목 **-200.7억원**, 국내건축 **-181.5억원**, 해외도급 **-169.7억원** 등이 이를 상쇄했습니다. 따라서 특정 부문의 증가만으로 회사 전체 현금전환을 판단하면 왜곡될 수 있습니다.")

    with st.expander("계약금액·총원가 추정 변경도 영향을 줬나?"):
        st.write("2025년 계약금액·총원가 추정 변경이 미청구공사(초과청구공사)에 미친 영향도 공시돼 있습니다. 국내주택에는 약 **+110.1억원**의 영향이 있었지만, 전체 영향은 약 **-143.1억원**이었습니다.")
        st.dataframe(estimate_change_2025.style.format({"추정변경_영향_억원":"{:+,.1f}"}), hide_index=True, use_container_width=True)
        st.write("따라서 국내주택 미청구공사 증가를 단순히 회계 추정 변경 하나로 설명할 수 없습니다. 공사 진행에 따른 매출 인식과 실제 청구 시점의 차이 등도 함께 작용한 것으로 해석해야 합니다.")

    st.markdown("""
    <div class="kolon-card">
    <b>이 탭에서 얻는 최종 결론</b><br><br>
    ① 주요 대형계약에서는 2025년 미청구공사가 크게 증가했고, 프로젝트별로 보면 삼성전자 평택 사무6동·대한항공 엔진정비공장·부산 기장 물류센터 등의 증가 영향이 컸습니다.<br>
    ② 그러나 전체 진행 중 건설계약으로 범위를 넓히면 미청구공사 총액은 전년과 거의 동일했습니다.<br>
    ③ 따라서 <b>코오롱글로벌 전체의 현금전환이 악화됐다고 단정하기보다는 일부 대형 프로젝트의 청구 전 잔액이 확대된 현상</b>으로 해석하는 것이 적절합니다.<br>
    ④ 실제 현금창출이 개선됐는지는 다음 탭의 <b>영업활동현금흐름과 운전자본 변동</b>을 통해 추가 검증합니다.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# TAB 4. 영업현금흐름 개선 분석
# -----------------------------
with tab4:
    st.subheader("④ 2025 영업현금흐름 개선 원인 분석")
    st.write(
        "2023~2025 연결 현금흐름표를 비교해 실제 영업현금흐름의 변화와 "
        "2025년 플러스 전환을 만든 운전자본 요인을 분석합니다."
    )

    o2023 = operating_cf.iloc[0]
    o2024 = operating_cf.iloc[1]
    o2025 = operating_cf.iloc[2]
    ocf_improvement = o2025["영업활동현금흐름_억원"] - o2024["영업활동현금흐름_억원"]
    wc_improvement = o2025["운전자본변동_억원"] - o2024["운전자본변동_억원"]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("2023 영업활동현금흐름", f"{o2023['영업활동현금흐름_억원']:,.0f}억원")
    k2.metric("2024 영업활동현금흐름", f"{o2024['영업활동현금흐름_억원']:,.0f}억원")
    k3.metric(
        "2025 영업활동현금흐름",
        f"{o2025['영업활동현금흐름_억원']:,.0f}억원",
        f"전년 대비 +{ocf_improvement:,.0f}억원"
    )
    k4.metric(
        "2025 운전자본 변동",
        f"+{o2025['운전자본변동_억원']:,.0f}억원",
        f"전년 대비 +{wc_improvement:,.0f}억원 개선"
    )

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=operating_cf["연도"],
        y=operating_cf["영업활동현금흐름_억원"],
        name="영업활동현금흐름",
        text=operating_cf["영업활동현금흐름_억원"].map(lambda x: f"{x:,.0f}")
    ))
    fig4.add_trace(go.Bar(
        x=operating_cf["연도"],
        y=operating_cf["영업에서창출된현금_억원"],
        name="영업에서 창출된 현금",
        text=operating_cf["영업에서창출된현금_억원"].map(lambda x: f"{x:,.0f}")
    ))
    fig4.update_traces(textposition="outside")
    fig4.update_layout(
        barmode="group",
        title="2023~2025 영업현금흐름 추이",
        yaxis_title="억원",
        legend_title_text="",
        hovermode="x unified"
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("#### 왜 2025년에 개선됐나? — 운전자본 변동")
    st.write(
        f"영업활동 관련 자산·부채 변동은 2024년 {o2024['운전자본변동_억원']:,.0f}억원의 "
        f"현금유출 효과에서 2025년 +{o2025['운전자본변동_억원']:,.0f}억원의 현금유입 효과로 전환됐습니다. "
        f"전년 대비 약 {wc_improvement:,.0f}억원 개선된 것입니다."
    )

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=operating_cf["연도"],
        y=operating_cf["운전자본변동_억원"],
        name="운전자본 변동",
        text=operating_cf["운전자본변동_억원"].map(lambda x: f"{x:,.0f}")
    ))
    fig5.add_trace(go.Bar(
        x=operating_cf["연도"],
        y=operating_cf["매출채권증감_현금효과_억원"],
        name="매출채권 증감의 현금효과",
        text=operating_cf["매출채권증감_현금효과_억원"].map(lambda x: f"{x:,.0f}")
    ))
    fig5.update_traces(textposition="outside")
    fig5.update_layout(
        barmode="group",
        title="운전자본 변동과 매출채권 현금부담",
        yaxis_title="억원",
        legend_title_text="",
        hovermode="x unified"
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("#### 2024 → 2025 운전자본 개선 요인 분해")
    bridge_sorted = wc_bridge.sort_values("전년대비_개선효과_억원", ascending=True)
    fig6 = px.bar(
        bridge_sorted,
        x="전년대비_개선효과_억원",
        y="항목",
        orientation="h",
        text="전년대비_개선효과_억원",
        labels={"전년대비_개선효과_억원": "2024 대비 현금흐름 개선효과(억원)", "항목": ""},
        title="항목별 2025 현금흐름 개선/악화 효과"
    )
    fig6.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig6.add_vline(x=0, line_width=1, line_dash="dash")
    st.plotly_chart(fig6, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="kolon-card">
        <b>가장 큰 개선 요인: 매입채무</b><br><br>
        2024년에는 매입채무 감소가 약 <b>2,193억원의 현금유출 효과</b>를 만들었지만,
        2025년에는 매입채무 증가가 약 <b>563억원의 현금유입 효과</b>로 바뀌었습니다.
        전년 대비 현금흐름 개선효과는 약 <b>2,756억원</b>으로,
        운전자본 개선을 설명하는 가장 큰 항목입니다.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="kolon-card">
        <b>매출채권 부담도 완화</b><br><br>
        매출채권 증가에 따른 현금유출 효과는
        <b>2023년 -3,236억원 → 2024년 -1,097억원 → 2025년 -756억원</b>으로 축소됐습니다.
        매출채권이 여전히 현금을 묶고 있지만, 증가에 따른 부담 규모는 3년 연속 완화됐습니다.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="kolon-note">
    <b>최종 결론</b><br><br>
    코오롱글로벌의 연결 영업활동현금흐름은 2023년 -1,484억원, 2024년 -2,133억원에서
    2025년 +724억원으로 플러스 전환했습니다. 핵심 배경은 단순한 손익 개선이라기보다
    <b>운전자본의 현금 부담이 크게 완화된 데 있습니다.</b><br><br>
    특히 2024년 대규모 현금유출 요인이었던 매입채무 변동이 2025년 현금유입 방향으로 전환됐고,
    매출채권 증가에 따른 현금유출 부담도 축소됐습니다. 이에 따라 영업활동 관련 자산·부채 변동은
    2024년 -1,571억원에서 2025년 +311억원으로 약 1,882억원 개선됐습니다.<br><br>
    따라서 2025년은 <b>수주와 매출 규모뿐 아니라 실제 영업활동에서 현금을 만들어내는 흐름이 개선된 해</b>로
    해석할 수 있습니다. 다만 연결 영업현금흐름은 건설·상사·레저 등 전체 사업의 결과이므로,
    이를 건설 고객의 현금회수 개선만으로 단정하지 않습니다.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("2024·2025 운전자본 세부 항목 보기"):
        wc_show = wc_bridge.copy()
        for col in ["2024_현금효과_억원", "2025_현금효과_억원", "전년대비_개선효과_억원"]:
            wc_show[col] = wc_show[col].map(lambda x: f"{x:,.0f}")
        wc_show.columns = ["항목", "2024 현금효과(억원)", "2025 현금효과(억원)", "전년 대비 개선효과(억원)"]
        st.dataframe(wc_show, hide_index=True, use_container_width=True)
        st.caption(
            "양수는 영업현금흐름에 플러스, 음수는 마이너스 효과를 의미합니다. "
            "전년 대비 개선효과는 2025 현금효과에서 2024 현금효과를 차감한 값입니다."
        )

# -----------------------------
# 출처 / 유의사항
# -----------------------------
st.divider()
with st.expander("데이터 출처 및 해석 유의사항"):
    st.markdown("""
    **출처**
    - 사용자가 제공한 2023·2024·2025 ㈜코오롱 사업보고서 내 코오롱글로벌 관련 공시
    - 2025 판매경로별 매출: 건설 2,307,978백만원, 상사 302,576백만원,
      레저 76,035백만원, AM 4,586백만원
    - 건설 신규수주: 2023년 3.1조원, 2024년 4.2조원,
      2025년 '약 3조원 돌파', 2025년 말 수주잔고 약 11.8조원
    - 주요 건설계약 합계:
      2023 미청구공사 78,962백만원 / 공사미수금 96,492백만원,
      2024 86,560백만원 / 154,741백만원,
      2025 123,523백만원 / 153,611백만원
    - 연결 영업활동현금흐름: 2023 -148,360백만원 / 2024 -213,267백만원 / 2025 +72,356백만원
    - 영업활동 관련 자산·부채 변동: 2023 -168,997백만원 / 2024 -157,062백만원 / 2025 +31,134백만원
    - 매출채권 증감의 현금효과: 2023 -323,572백만원 / 2024 -109,681백만원 / 2025 -75,590백만원

    **유의사항**
    - 이 도구는 공시자료를 구조화해 관계를 빠르게 파악하기 위한 개인 분석 프로젝트입니다.
    - 주요계약 표의 미청구공사·공사미수금 합계는 회사 전체 계정잔액과 동일하지 않습니다.
    - 전체 진행 중 건설계약 미청구공사: 2024년 299,432백만원 / 2025년 298,287백만원
    - 2025년 전체 미청구공사 부문별 잔액: 국내토목 72,535 / 국내건축 30,185 / 국내플랜트 16,152 / 국내주택 147,748 / 국내환경 8,701 / 해외도급 22,966백만원
    - 수주잔고는 향후 매출의 참고지표이며, 계약 변경·공정·원가·해지 등에 따라 실제 매출 인식 시점과 금액이 달라질 수 있습니다.
    - 특정 수치만으로 부실·위험 여부를 단정하지 않습니다.
    """)

st.caption("KOLON Global Financial Insight · 개인 재무분석 프로젝트")
