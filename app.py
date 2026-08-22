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

# 3) 주요 건설계약 기준 미청구공사 / 공사미수금
# '계약금액이 전기 매출액의 5% 이상인 주요 계약' 표의 합계치
cash_conversion = pd.DataFrame({
    "연도": ["2023", "2024", "2025"],
    "미청구공사_억원": [789.62, 865.60, 1235.23],
    "공사미수금_억원": [964.92, 1547.41, 1536.11]
})
cash_conversion["합계_억원"] = (
    cash_conversion["미청구공사_억원"] +
    cash_conversion["공사미수금_억원"]
)
cash_conversion["전년대비_증감률"] = cash_conversion["합계_억원"].pct_change() * 100

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
→ ③ 주요 건설계약에서 매출 인식 이후 회수 관련 계정은 어떻게 움직이는가
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "① 사업 포트폴리오",
    "② 수주 → 매출",
    "③ 현금전환 분석"
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
    st.subheader("③ 주요 건설계약 현금전환 분석")
    st.write(
        "매출 자체보다, 공사 진행 과정에서 발생하는 미청구공사와 공사미수금의 "
        "변화를 함께 확인합니다."
    )

    st.caption(
        "주의: 아래 금액은 코오롱글로벌 전체 미청구공사·공사미수금이 아니라, "
        "사업보고서의 '계약금액이 전기 매출액의 5% 이상인 주요 건설계약' 표에 기재된 합계입니다."
    )

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=cash_conversion["연도"],
        y=cash_conversion["미청구공사_억원"],
        name="미청구공사"
    ))
    fig3.add_trace(go.Bar(
        x=cash_conversion["연도"],
        y=cash_conversion["공사미수금_억원"],
        name="공사미수금"
    ))
    fig3.update_layout(
        barmode="group",
        title="주요 건설계약 기준 미청구공사·공사미수금",
        yaxis_title="억원",
        legend_title_text=""
    )
    st.plotly_chart(fig3, use_container_width=True)

    latest = cash_conversion.iloc[-1]
    prev = cash_conversion.iloc[-2]

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "2025 주요계약 미청구공사",
        f"{latest['미청구공사_억원']:,.0f}억원",
        f"{(latest['미청구공사_억원']/prev['미청구공사_억원']-1)*100:.1f}%"
    )
    col2.metric(
        "2025 주요계약 공사미수금",
        f"{latest['공사미수금_억원']:,.0f}억원",
        f"{(latest['공사미수금_억원']/prev['공사미수금_억원']-1)*100:.1f}%"
    )
    col3.metric(
        "2025 두 계정 합계",
        f"{latest['합계_억원']:,.0f}억원",
        f"{latest['전년대비_증감률']:.1f}%"
    )

    st.markdown("""
    <div class="kolon-note">
    <b>자동 해석</b><br>
    2025년 주요 계약 기준 미청구공사는 전년 대비 증가한 반면,
    공사미수금은 전년과 유사한 수준입니다.
    두 계정은 곧바로 부실을 의미하지 않으며, 공사진행률·청구조건·발주처의 지급능력과
    함께 회수 추이를 확인해야 합니다.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("왜 미청구공사와 공사미수금을 같이 보나요?"):
        st.markdown("""
        - **미청구공사**: 공사진행에 따라 수익은 인식했지만 아직 발주처에 청구하지 못한 금액을 보는 데 활용할 수 있습니다.
        - **공사미수금**: 청구 이후 아직 회수되지 않은 금액의 추이를 보는 데 활용할 수 있습니다.
        - 따라서 `수주 → 공사진행 → 매출 인식 → 청구 → 회수` 흐름에서 어느 구간에 금액이 쌓이는지 확인하는 보조지표로 사용할 수 있습니다.
        - 감사보고서에서도 미청구공사의 회수가능성 평가는 중요한 판단 영역으로 다뤄집니다.
        """)

    st.markdown("#### 2025 주요 프로젝트 예시")
    st.dataframe(
        projects_2025.style.format({
            "수주총액_억원": "{:,.0f}",
            "진행률_%": "{:.2f}",
            "미청구공사_억원": "{:,.2f}",
            "공사미수금_억원": "{:,.2f}"
        }),
        hide_index=True,
        use_container_width=True
    )

    selected = st.selectbox("프로젝트 상세 보기", projects_2025["프로젝트"].tolist())
    row = projects_2025[projects_2025["프로젝트"] == selected].iloc[0]

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("수주총액", f"{row['수주총액_억원']:,.0f}억원")
    p2.metric("진행률", f"{row['진행률_%']:.2f}%")
    p3.metric("미청구공사", f"{row['미청구공사_억원']:,.2f}억원")
    p4.metric("공사미수금", f"{row['공사미수금_억원']:,.2f}억원")

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

    **유의사항**
    - 이 도구는 공시자료를 구조화해 관계를 빠르게 파악하기 위한 개인 분석 프로젝트입니다.
    - 주요계약 표의 미청구공사·공사미수금 합계는 회사 전체 계정잔액과 동일하지 않습니다.
    - 수주잔고는 향후 매출의 참고지표이며, 계약 변경·공정·원가·해지 등에 따라 실제 매출 인식 시점과 금액이 달라질 수 있습니다.
    - 특정 수치만으로 부실·위험 여부를 단정하지 않습니다.
    """)

st.caption("KOLON Global Financial Insight · 개인 재무분석 프로젝트")
