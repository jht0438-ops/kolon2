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

# 1) 사업 포트폴리오 - 별도기준 매출
# 2023·2024·2025 사업보고서의 동일 기준 비교 (원자료 단위: 백만원 → 억원 환산)
portfolio_by_year = pd.DataFrame({
    "연도": ["2023", "2023", "2023", "2023",
             "2024", "2024", "2024", "2024",
             "2025", "2025", "2025", "2025"],
    "사업부문": ["건설", "상사", "레저", "AM"] * 3,
    "매출액_억원": [
        21494.52, 3827.96, 576.56, 0.00,
        24384.78, 3365.24, 649.87, 0.00,
        23079.77, 3025.75, 760.35, 45.86
    ]
})
portfolio_by_year["연도총매출_억원"] = portfolio_by_year.groupby("연도")["매출액_억원"].transform("sum")
portfolio_by_year["비중"] = portfolio_by_year["매출액_억원"] / portfolio_by_year["연도총매출_억원"] * 100
portfolio = portfolio_by_year[portfolio_by_year["연도"] == "2025"].copy()

# 2) 건설 신규수주 및 수주잔고
orders = pd.DataFrame({
    "연도": ["2023", "2024", "2025"],
    "전체_신규수주_조원": [3.1, 4.2, 3.0],
    "비주택_신규수주_조원": [1.6, 2.3, 1.7],
})
orders["주택_신규수주_조원"] = orders["전체_신규수주_조원"] - orders["비주택_신규수주_조원"]
orders["비주택_비중_%"] = orders["비주택_신규수주_조원"] / orders["전체_신규수주_조원"] * 100

nonhousing_detail = pd.DataFrame({
    "구분": ["건축", "토목", "환경·플랜트"],
    "2023": [0.7, 0.4, 0.5],
    "2024": [0.9, 1.0, 0.4],
})

backlog = pd.DataFrame({
    "연도": ["2023", "2024", "2025"],
    "수주잔고_조원": [10.96, 11.66, 11.8]
})
backlog_2025 = 11.8
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
st.caption("코오롱글로벌의 사업구조 → 신규수주 구성 → 수주잔고·매출 → 청구 전 잔액을 연결해 보는 재무분석 대시보드")

m1, m2, m3, m4 = st.columns(4)
m1.metric("2025 총매출", "2조 6,912억원")
m2.metric("건설 매출 비중", "85.8%")
m3.metric("2025 건설 수주잔고", "약 11.8조원")
m4.metric("수주잔고 ÷ 건설매출", f"약 {backlog_years:.1f}배")

st.markdown("""
<div class="kolon-note">
<b>분석 방향</b><br>
① 코오롱글로벌은 어디서 매출을 만드는가 → ② 신규수주의 주택·비주택 구성이 어떻게 변하는가
→ ③ 확보한 수주가 수주잔고와 미래 매출 기반으로 어떻게 이어지는가
→ ④ 매출 인식 후 청구 전 단계의 미청구공사는 어디에서 증가했는가<br>
⑤ 높은 건설 의존도를 완화하기 위해 어떤 사업에 자원을 배분할 것인가
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "① 사업 포트폴리오",
    "② 신규수주 → 수주잔고 → 매출",
    "③ 매출 → 청구 → 회수",
    "④ 다각화 후보",
    "⑤ 비건설 사업 검증",
    "⑥ 비주택 성장축 검증",
    "⑦ 자원배분 제언"
])

# -----------------------------
# TAB 1. 사업 포트폴리오
# -----------------------------
with tab1:
    st.subheader("① 사업 포트폴리오 분석")
    st.write("2025년 사업부문별 매출을 먼저 확인하고, 버튼을 누르면 2023~2025년 최근 3개년의 사업구조 변화를 동일 기준으로 비교할 수 있습니다.")

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
        df_show["비중표시"] = df_show["비중"].map(lambda x: f"{x:.1f}%")
        st.dataframe(
            df_show[["사업부문", "매출액", "비중표시"]].rename(columns={"비중표시":"비중"}),
            hide_index=True,
            use_container_width=True
        )

        st.markdown("""
        <div class="kolon-card">
        <b>2025년 해석</b><br><br>
        2025년 별도기준 매출의 약 <b>85.8%</b>가 건설부문에서 발생합니다.
        따라서 코오롱글로벌 전체 재무를 이해할 때 건설사업의
        수주, 매출 인식, 청구 관련 계정을 우선적으로 살펴볼 필요가 있습니다.<br><br>
        상사는 약 11.2%, 레저는 약 2.8%, AM은 약 0.2%를 차지합니다.
        </div>
        """, unsafe_allow_html=True)

    st.caption("기준: 별도재무제표 사업부문별 매출. 2025년 AM은 2025년 12월 합병 이후 1개월 실적이 포함되어 있습니다.")

    if "show_three_year_portfolio" not in st.session_state:
        st.session_state.show_three_year_portfolio = False

    if st.button("최근 3개년 함께 비교하기", use_container_width=True):
        st.session_state.show_three_year_portfolio = not st.session_state.show_three_year_portfolio

    if st.session_state.show_three_year_portfolio:
        st.markdown("---")
        st.markdown("### 2023~2025 사업 포트폴리오 변화")
        st.write("각 연도의 총매출뿐 아니라 건설·상사·레저가 전체 매출에서 차지하는 비중이 어떻게 달라졌는지 함께 확인합니다.")

        totals = portfolio_by_year.groupby("연도", as_index=False)["매출액_억원"].sum()
        t1, t2, t3 = st.columns(3)
        t1.metric("2023 총매출", f"{totals.loc[totals['연도']=='2023','매출액_억원'].iloc[0]:,.0f}억원")
        t2.metric("2024 총매출", f"{totals.loc[totals['연도']=='2024','매출액_억원'].iloc[0]:,.0f}억원", "+9.7%")
        t3.metric("2025 총매출", f"{totals.loc[totals['연도']=='2025','매출액_억원'].iloc[0]:,.0f}억원", "-5.2%")

        fig_mix = px.bar(
            portfolio_by_year,
            x="연도", y="매출액_억원", color="사업부문",
            barmode="stack",
            text_auto=".3s",
            labels={"매출액_억원":"매출액(억원)", "연도":"", "사업부문":"사업부문"},
            title="최근 3개년 사업부문별 매출액"
        )
        fig_mix.update_layout(margin=dict(t=60, b=20, l=20, r=20))
        st.plotly_chart(fig_mix, use_container_width=True)

        pivot_share = portfolio_by_year.pivot(index="사업부문", columns="연도", values="비중").reset_index()
        order_map = {"건설":0, "상사":1, "레저":2, "AM":3}
        pivot_share["_order"] = pivot_share["사업부문"].map(order_map)
        pivot_share = pivot_share.sort_values("_order").drop(columns="_order")
        for y in ["2023", "2024", "2025"]:
            pivot_share[y] = pivot_share[y].map(lambda x: f"{x:.1f}%")
        st.markdown("#### 사업부문별 매출 비중")
        st.dataframe(pivot_share, hide_index=True, use_container_width=True)

        construction = portfolio_by_year[portfolio_by_year["사업부문"] == "건설"].copy()
        trading = portfolio_by_year[portfolio_by_year["사업부문"] == "상사"].copy()
        leisure = portfolio_by_year[portfolio_by_year["사업부문"] == "레저"].copy()

        st.markdown(f"""
        <div class="kolon-card">
        <b>3개년에서 얻는 결론</b><br><br>
        ① 건설 매출은 <b>2023년 {construction.iloc[0]['매출액_억원']:,.0f}억원 → 2024년 {construction.iloc[1]['매출액_억원']:,.0f}억원 → 2025년 {construction.iloc[2]['매출액_억원']:,.0f}억원</b>으로, 2024년 확대 후 2025년 감소했습니다.<br><br>
        ② 전체 매출에서 건설이 차지하는 비중은 <b>2023년 {construction.iloc[0]['비중']:.1f}% → 2024년 {construction.iloc[1]['비중']:.1f}% → 2025년 {construction.iloc[2]['비중']:.1f}%</b>로 높은 수준을 유지했습니다. 즉 최근 3개년 재무구조를 분석할 때 건설부문을 중심에 두는 근거가 더욱 명확합니다.<br><br>
        ③ 상사 매출은 <b>2023년 {trading.iloc[0]['매출액_억원']:,.0f}억원 → 2025년 {trading.iloc[2]['매출액_억원']:,.0f}억원</b>으로 감소한 반면, 레저 매출은 <b>{leisure.iloc[0]['매출액_억원']:,.0f}억원 → {leisure.iloc[2]['매출액_억원']:,.0f}억원</b>으로 증가했습니다.<br><br>
        ④ 따라서 다음 탭에서는 회사 실적에 가장 큰 영향을 주는 <b>건설부문의 신규수주 구성과 수주잔고</b>를 집중적으로 분석합니다.
        </div>
        """, unsafe_allow_html=True)

        st.info("비교 시 유의: 2023·2024년 레저는 당시 스포렉스 중심 실적이며, 2025년에는 12월 합병으로 편입된 레저·AM 사업의 1개월 실적이 포함되어 있어 사업범위가 완전히 동일하지는 않습니다.")

# -----------------------------
# TAB 2. 신규수주 → 수주잔고 → 매출
# -----------------------------
with tab2:
    st.subheader("② 신규수주 구성 → 수주잔고 → 매출 분석")
    st.write("총수주액만 보는 대신, 새로 확보한 일감의 구성과 비주택 확대 흐름을 확인한 뒤 수주잔고와 미래 매출 기반으로 연결합니다.")

    st.markdown("#### 1. 2023~2025 신규수주: 얼마나 확보했나?")
    a, b, c = st.columns(3)
    a.metric("2023 신규수주", "약 3.1조원")
    b.metric("2024 신규수주", "약 4.2조원", "+35.5%")
    c.metric("2025 신규수주", "약 3.0조원", "-28.6%")

    fig_total = px.bar(orders, x="연도", y="전체_신규수주_조원", text="전체_신규수주_조원",
                       labels={"전체_신규수주_조원":"신규수주(조원)", "연도":""}, title="전체 신규수주 추이")
    fig_total.update_traces(texttemplate="%{text:.1f}조", textposition="outside")
    fig_total.update_layout(yaxis_range=[0, 5.0])
    st.plotly_chart(fig_total, use_container_width=True)

    st.markdown("""<div class="kolon-card"><b>해석</b><br><br>
    2024년 신규수주는 약 <b>4.2조원</b>으로 2023년 대비 크게 확대됐습니다. 2025년은 약 <b>3.0조원</b>으로 전년보다 감소했습니다.
    다만 총액만으로는 회사가 어떤 사업을 중심으로 수주 포트폴리오를 바꾸고 있는지 알기 어렵기 때문에 주택·비주택 구성을 함께 봅니다.
    </div>""", unsafe_allow_html=True)

    st.markdown("#### 2. 주택 vs 비주택: 수주 포트폴리오는 어떻게 변했나?")
    fig_mix = go.Figure()
    fig_mix.add_trace(go.Bar(x=orders["연도"], y=orders["주택_신규수주_조원"], name="주택 신규수주", text=orders["주택_신규수주_조원"].map(lambda x:f"{x:.1f}조")))
    fig_mix.add_trace(go.Bar(x=orders["연도"], y=orders["비주택_신규수주_조원"], name="비주택 신규수주", text=orders["비주택_신규수주_조원"].map(lambda x:f"{x:.1f}조")))
    fig_mix.update_layout(barmode="stack", title="신규수주 주택·비주택 구성", yaxis_title="조원", legend_title_text="")
    fig_mix.update_traces(textposition="inside")
    st.plotly_chart(fig_mix, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("2023 비주택", "1.6조원", f"비중 {orders.loc[0,'비주택_비중_%']:.1f}%")
    m2.metric("2024 비주택", "2.3조원", "+43.8% / 비중 54.8%")
    m3.metric("2025 비주택", "1.7조원", f"비중 {orders.loc[2,'비주택_비중_%']:.1f}%")

    st.markdown("""<div class="kolon-note"><b>여기서 얻는 결론</b><br><br>
    2024년 비주택 신규수주는 <b>1.6조원 → 2.3조원으로 약 43.8% 증가</b>했고 전체 신규수주의 절반 이상을 차지했습니다.
    2025년에도 전체 신규수주 약 3조원 가운데 비주택이 <b>1.7조원, 약 56.7%</b>를 차지합니다.
    즉 2025년 총 신규수주는 전년보다 줄었지만 <b>비주택이 신규수주의 절반 이상을 차지하는 구성은 유지</b>됐습니다.
    </div>""", unsafe_allow_html=True)

    st.markdown("#### 3. 2024년 비주택 수주 확대는 어디에서 나왔나?")
    detail_long = nonhousing_detail.melt(id_vars="구분", value_vars=["2023","2024"], var_name="연도", value_name="신규수주_조원")
    fig_detail = px.bar(detail_long, x="구분", y="신규수주_조원", color="연도", barmode="group", text="신규수주_조원",
                        labels={"신규수주_조원":"신규수주(조원)","구분":""}, title="비주택 신규수주 세부 구성(회사 IR의 반올림 수치)")
    fig_detail.update_traces(texttemplate="%{text:.1f}조", textposition="outside")
    st.plotly_chart(fig_detail, use_container_width=True)

    st.markdown("""<div class="kolon-card"><b>비주택 증가의 핵심</b><br><br>
    회사 IR의 반올림 수치 기준으로 2023→2024 비주택 신규수주는 건축 <b>0.7→0.9조원</b>, 토목 <b>0.4→1.0조원</b>, 환경·플랜트 <b>0.5→0.4조원</b>으로 변화했습니다.
    따라서 2024년 비주택 확대에서 가장 두드러진 변화는 <b>토목 수주의 확대</b>입니다.
    </div>""", unsafe_allow_html=True)

    st.markdown("#### 4. 확보한 수주는 수주잔고로 얼마나 남아 있나?")
    fig_backlog = px.line(backlog, x="연도", y="수주잔고_조원", markers=True, text="수주잔고_조원",
                          labels={"수주잔고_조원":"수주잔고(조원)","연도":""}, title="연말 수주잔고 추이")
    fig_backlog.update_traces(texttemplate="%{text:.2f}조", textposition="top center")
    fig_backlog.update_layout(yaxis_range=[10, 12.5])
    st.plotly_chart(fig_backlog, use_container_width=True)

    q1, q2, q3 = st.columns(3)
    q1.metric("2023 수주잔고", "약 10.96조원")
    q2.metric("2024 수주잔고", "약 11.66조원", "+6.4%")
    q3.metric("2025 수주잔고", "약 11.8조원", "+1.2%")

    st.markdown(f"""<div class="kolon-note"><b>수주 → 미래 매출 기반</b><br><br>
    신규수주는 연도별로 변동했지만 연말 수주잔고는 <b>2023년 약 10.96조원 → 2024년 11.66조원 → 2025년 약 11.8조원</b>으로 확대됐습니다.
    2025년 수주잔고는 당해 건설매출 약 2.31조원의 <b>약 {backlog_years:.1f}배</b>입니다. 이는 현재 매출 규모와 비교한 미래 사업 기반의 참고지표입니다.
    다만 수주잔고는 계약변경·공정·원가·해지 등에 따라 변할 수 있으므로 동일 금액의 미래 매출을 보장하지 않습니다.
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="kolon-card"><b>이 탭의 최종 결론</b><br><br>
    ① 2024년 신규수주는 4.2조원으로 크게 확대됐고 비주택 신규수주가 1.6조원에서 2.3조원으로 증가했습니다.<br>
    ② 특히 2024년 비주택 확대에서는 토목 수주의 증가가 두드러졌습니다.<br>
    ③ 2025년 신규수주 총액은 약 3조원으로 감소했지만 비주택은 1.7조원으로 전체의 약 56.7%를 차지했습니다.<br>
    ④ 연말 수주잔고는 3년간 확대돼 2025년 약 11.8조원에 이르렀습니다. 즉 <b>신규수주 총액의 변동 속에서도 비주택 중심의 수주 구성과 누적 수주잔고를 통해 향후 매출 기반을 확보하는 흐름</b>을 확인할 수 있습니다.
    </div>""", unsafe_allow_html=True)

    st.caption("신규수주는 회사가 제시한 신규수주 기준이며 회계 주석의 '당기 계약액(신규수주+계약변경 등)'과 구분합니다. 세부 비주택 수치는 회사 IR의 반올림 수치입니다.")

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
    ④ 공개자료만으로 실제 현금전환율을 직접 계산하기는 어렵기 때문에, 이 탭은 <b>매출 인식 후 청구 전 단계와 청구 후 회수 전 단계의 잔액이 어디에 쌓이는지</b>를 진단하는 데 초점을 둡니다.
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# TAB 4~7. 사업 다각화 확장 분석
# -----------------------------
# 분석 원칙: 결론을 먼저 정하지 않고, 공시 수치 → 실제 사업성과 → 보완자료 순으로 후보를 검증

# 2026년 1분기 사업부문별 매출(억원, 공시자료 구조화)
portfolio_2026q1 = pd.DataFrame({
    "사업부문": ["건설", "상사", "레저", "AM"],
    "매출액_억원": [5232.38, 431.24, 453.11, 195.37]
})
portfolio_2026q1["비중_%"] = portfolio_2026q1["매출액_억원"] / portfolio_2026q1["매출액_억원"].sum() * 100

# 상사부문 3개년 매출: 동일 기준으로 성장 방향성 검증
trading_trend = portfolio_by_year[portfolio_by_year["사업부문"] == "상사"][["연도", "매출액_억원"]].copy()
trading_trend["전년대비_%"] = trading_trend["매출액_억원"].pct_change() * 100
trading_23_25_change = (trading_trend.iloc[-1]["매출액_억원"] / trading_trend.iloc[0]["매출액_억원"] - 1) * 100

# 2026년 1분기 회사 발표 핵심 실적: 레저·AM 통합 효과 검증
leisure_am_q1 = {
    "매출_억원": 649,
    "매출증가율_%": 344.5,
    "영업이익_상태": "흑자전환"
}

# 비주택 수주 심층분석
# 원칙: 회사가 공개한 전체 비주택 신규수주와 개별 식별 가능한 프로젝트를 구분한다.
# 사업보고서의 '당기 계약액'은 신규수주+계약변경 등이 포함되므로 신규수주액으로 합산하지 않는다.
nonhousing_total = pd.DataFrame({
    "기간": ["2023", "2024", "2025", "2026 H1"],
    "전체_신규수주_억원": [31000, 42000, 30572, 9854],
    "비주택_신규수주_억원": [16000, 23000, 16586, 4753],
})
nonhousing_total["비주택_비중_%"] = nonhousing_total["비주택_신규수주_억원"] / nonhousing_total["전체_신규수주_억원"] * 100

# 공개자료에서 개별적으로 확인되는 대표 비주택 프로젝트.
# '신규수주'만 비중 계산에 사용하고, 계약변경/현재계약액은 별도 참고로만 표시한다.
nonhousing_projects = pd.DataFrame([
    ["2023", "삼성 평택 고덕 공공폐수처리시설(4-1단계)", "첨단·산업시설 Value Chain", "반도체 인프라·수처리", 1427, "현재 계약액", "사업보고서 계약표"],
    ["2024", "삼성전자 평택 P5 정수장", "첨단·산업시설 Value Chain", "반도체 인프라·수처리", 2975, "신규수주", "회사 공개자료"],
    ["2024", "머크 바이오시설", "첨단·산업시설 Value Chain", "바이오 생산시설", 1766, "신규수주", "회사 공개자료"],
    ["2024", "대한항공 엔진정비공장", "첨단·산업시설 Value Chain", "항공 MRO 산업시설", 3143, "현재 계약액", "사업보고서 계약표"],
    ["2024", "정읍 21.9MW 바이오매스 발전사업", "에너지·신재생", "바이오매스 발전", 1496, "신규수주", "회사 공개자료"],
    ["2024", "춘천-속초·강릉-제진 철도 관련 공사", "공공 인프라", "철도·토목", 1593, "현재 계약액", "사업보고서 계약표"],
    ["2025", "삼성전자 평택1단지 방류수온저감시설", "첨단·산업시설 Value Chain", "반도체 인프라·수처리", 733, "공개 수주", "회사/언론 공개자료"],
    ["2025", "머크 BIOP 설계변경", "첨단·산업시설 Value Chain", "바이오 생산시설", 517, "계약변경", "공개자료 - 신규수주 합산 제외"],
    ["2025", "도쿄일렉트론코리아 연구시설", "첨단·산업시설 Value Chain", "반도체 장비 연구시설", 1271, "공개 수주", "회사/언론 공개자료"],
    ["2026 H1", "용인 반도체 산업단지 통합용수공급사업", "첨단·산업시설 Value Chain", "반도체 인프라·용수", 1265, "신규수주", "2026 H1 회사 발표"],
    ["2026 H1", "금호타이어 제조공장", "첨단·산업시설 Value Chain", "제조 산업시설", 399, "신규수주", "2026 H1 회사 발표"],
    ["2026 H1", "울진 기성 풍력단지", "에너지·신재생", "풍력", 770, "신규수주", "2026 Q1 회사 발표"],
], columns=["기간","프로젝트","대분류","세부분류","금액_억원","금액성격","근거"] )

# 2026 H1은 전체 비주택 신규수주와 개별 신규수주가 동시에 공개되어 '확인 가능한 최소 구성비' 계산이 가능
nh26 = nonhousing_total.loc[nonhousing_total["기간"]=="2026 H1", "비주택_신규수주_억원"].iloc[0]
identified_26 = nonhousing_projects[(nonhousing_projects["기간"]=="2026 H1") & (nonhousing_projects["금액성격"]=="신규수주")].groupby("대분류", as_index=False)["금액_억원"].sum()
identified_26["비주택수주_내_확인비중_%"] = identified_26["금액_억원"] / nh26 * 100
identified_26_total = identified_26["금액_억원"].sum()
identified_26_coverage = identified_26_total / nh26 * 100
unclassified_26 = nh26 - identified_26_total

# 최종 제언은 앞 탭의 검증 결과만 사용
allocation_logic = pd.DataFrame({
    "영역": ["첨단·산업시설 Value Chain", "공공 인프라", "에너지·신재생", "레저·AM"],
    "확인된 근거": [
        "반도체·바이오·항공MRO·제조시설과 용수/폐수 프로젝트 반복 확인",
        "철도·토목 등 기존 비주택 수행 및 수주잔고 기반",
        "바이오매스·풍력 실제 프로젝트 및 2026 H1 풍력 신규수주 확인",
        "2026년 합병효과와 실제 매출·영업이익 기여 확인"
    ],
    "해석": [
        "첨단시설 시공과 수처리 기술을 하나의 고객 Value Chain으로 연결 가능",
        "비주택 기반을 지탱하는 기존 인프라 축",
        "실제 사업화가 확인된 친환경에너지 축",
        "건설 프로젝트와 다른 운영수익 축"
    ],
    "제언 가능한 자원": [
        "하이테크 전문인력·수처리 R&D·기업고객 수주역량",
        "선별수주·원가/공정관리 역량",
        "개발 파이프라인·사업성 검증·EPC 역량",
        "운영효율화·장기 위탁운영 계약"
    ]
})

with tab4:
    st.subheader("④ 기존 분석에서 '어디에 더 투자할 것인가'로")
    st.markdown("""
    <div class="kolon-note">
    <b>앞의 3개 탭에서 새 질문이 생긴 이유</b><br><br>
    앞에서는 <b>사업별 매출 구성 → 신규수주 → 수주잔고 → 매출 → 미청구공사 → 공사미수금</b>을 연결했습니다.
    이를 통해 건설사업은 수주 규모만이 아니라 실제 매출 인식과 청구·회수까지 함께 봐야 한다는 점을 확인했습니다.<br><br>
    동시에 2025년 매출의 대부분이 여전히 건설에서 발생하는 반면, 신규수주의 절반 이상은 비주택이 차지했습니다.
    따라서 여기서부터는 분석을 한 단계 확장해 <b>“주택 의존도를 낮추기 위한 추가 성장자원을 어느 사업에 배분할 것인가?”</b>를 검증합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. 처음부터 후보를 정하지 않는다")
    candidate_pool = pd.DataFrame({
        "후보": ["상사", "레저", "AM", "산업·하이테크", "환경·수처리", "풍력·신재생"],
        "구분": ["건설 외", "건설 외", "건설 외", "건설 내부 비주택", "건설 내부 비주택", "건설 내부 비주택"],
        "우선 검증할 지표": [
            "최근 3개년 매출 방향성", "합병 이후 실제 실적", "합병 이후 실제 실적·사업모델",
            "실제 수주·프로젝트·조직", "프로젝트·R&D", "실제 수주·사업경험"
        ]
    })
    st.dataframe(candidate_pool, hide_index=True, use_container_width=True)

    st.markdown("### 2. 1차 탈락: 상사는 왜 추가 성장투자 후보에서 제외했나?")
    fig_trade = px.line(trading_trend, x="연도", y="매출액_억원", markers=True, text="매출액_억원",
                        title="상사부문 매출 추이", labels={"매출액_억원":"매출액(억원)", "연도":""})
    fig_trade.update_traces(texttemplate="%{text:,.0f}억원", textposition="top center")
    fig_trade.update_layout(yaxis_range=[0, 4500])
    st.plotly_chart(fig_trade, use_container_width=True)

    a,b,c,d = st.columns(4)
    a.metric("2023 상사 매출", f"{trading_trend.iloc[0]['매출액_억원']:,.0f}억원")
    b.metric("2024 상사 매출", f"{trading_trend.iloc[1]['매출액_억원']:,.0f}억원", f"{trading_trend.iloc[1]['전년대비_%']:.1f}%")
    c.metric("2025 상사 매출", f"{trading_trend.iloc[2]['매출액_억원']:,.0f}억원", f"{trading_trend.iloc[2]['전년대비_%']:.1f}%")
    d.metric("2023→2025", f"{trading_23_25_change:.1f}%", "매출 변화")

    st.markdown(f"""
    <div class="kolon-card">
    <b>판단: 상사 → 추가 성장투자 후보에서 1차 제외</b><br><br>
    상사 매출은 <b>2023년 {trading_trend.iloc[0]['매출액_억원']:,.0f}억원 → 2024년 {trading_trend.iloc[1]['매출액_억원']:,.0f}억원 → 2025년 {trading_trend.iloc[2]['매출액_억원']:,.0f}억원</b>으로 2년 연속 감소했습니다.
    2023년 대비 2025년 감소폭은 약 <b>{abs(trading_23_25_change):.1f}%</b>입니다.<br><br>
    이는 상사사업 자체를 축소해야 한다는 뜻이 아닙니다. 2025년에도 전체 매출에서 의미 있는 비중을 차지하는 기존 사업입니다.
    다만 이 분석의 목적은 <b>주택 의존도를 낮추기 위해 추가 성장자원을 어디에 배분할지</b> 찾는 것이므로,
    최근 3개년 매출에서 성장 확대 흐름이 확인되지 않은 상사는 이후의 <b>추가 성장투자 후보 비교에서 제외</b>합니다.
    </div>
    """, unsafe_allow_html=True)

    st.info("남은 후보: 레저 · AM · 산업·하이테크 · 환경·수처리 · 풍력·신재생")

with tab5:
    st.subheader("⑤ 건설 외 후보 검증: 레저·AM은 실제로 역할이 커졌나?")
    st.write("상사를 제외한 뒤, 레저·AM은 '반복수익일 것 같다'는 추정이 아니라 합병 이후 실제 실적과 회사가 제시한 운영수익 구조를 확인합니다.")

    c1,c2,c3 = st.columns(3)
    c1.metric("2026년 1Q 레저·AM 매출", f"{leisure_am_q1['매출_억원']:,.0f}억원")
    c2.metric("전년동기 대비", f"+{leisure_am_q1['매출증가율_%']:.1f}%")
    c3.metric("영업이익", leisure_am_q1["영업이익_상태"])

    st.markdown("""
    <div class="kolon-card">
    <b>왜 후보로 남기는가?</b><br><br>
    ① 2025년 말 LSI·MOD 합병 이후 2026년 1분기 <b>레저·AM 합산 매출은 649억원</b>으로 전년동기 대비 <b>344.5% 증가</b>했고 영업이익도 <b>흑자전환</b>했습니다.<br><br>
    ② 회사는 합병 이후 레저·AM을 건설과 다른 <b>운영수익</b> 축으로 설명하고 있습니다. 즉 수주 후 준공으로 종료되는 건설 프로젝트와 수익 발생 방식이 다릅니다.<br><br>
    ③ 따라서 레저·AM은 단순히 '새로 생긴 사업'이라서가 아니라, <b>실제 실적 기여가 확인됐고 건설 의존도를 보완할 수 있는 다른 수익구조</b>라는 점에서 후보로 유지합니다.
    </div>
    """, unsafe_allow_html=True)

    st.warning("주의: 2025년 말 합병으로 사업범위가 크게 달라졌기 때문에 2025년 연간 레저·AM 매출과 2026년 실적을 단순 성장률로 비교하지 않습니다. 또한 회사 발표에서 레저·AM을 합산해 설명하는 경우가 있어 두 사업의 개별 수익성을 임의로 분리하지 않습니다.")

    st.markdown("### 레저와 AM을 똑같이 보지는 않는다")
    compare_la = pd.DataFrame({
        "구분": ["레저", "AM"],
        "사업구조": ["골프·리조트·호텔 등 운영", "부동산 위탁운영·건물 유지관리"],
        "현재 확인 가능한 강점": ["합병으로 운영사업 규모 확대", "건설과 연계 가능한 시설운영·유지관리"],
        "공개자료 한계": ["개별 수익성 분리 확인 제한", "개별 수익성 분리 확인 제한"],
        "다음 판단": ["운영수익 후보 유지", "건설과 연계되는 운영수익 후보로 중점 검증"]
    })
    st.dataframe(compare_la, hide_index=True, use_container_width=True)

    st.markdown("""
    <div class="kolon-note"><b>5번 탭 결론</b><br><br>
    레저·AM은 2026년 실제 실적 기여가 확인되므로 후보로 남깁니다. 다만 공개자료만으로 레저와 AM의 개별 영업이익률을 비교할 수 없으므로
    <b>‘AM이 레저보다 수익성이 높다’고 판단하지 않습니다.</b> AM은 건설 준공 이후 시설운영·유지관리로 연결할 수 있다는 사업 연계성 때문에 최종 자원배분 단계에서 별도로 살펴봅니다.
    </div>
    """, unsafe_allow_html=True)

with tab6:
    st.subheader("⑥ 비주택 수주를 전부의 관점에서 다시 분해")
    st.write("특정 프로젝트 몇 건을 보고 결론을 내리지 않습니다. 먼저 회사가 공개한 비주택 신규수주 전체 규모를 놓고, 공개자료에서 개별 식별 가능한 프로젝트를 같은 기준으로 분류합니다.")

    st.markdown("### 1. 전체 신규수주에서 비주택은 얼마나 커졌나?")
    nh_show = nonhousing_total.copy()
    nh_show["전체 신규수주"] = nh_show["전체_신규수주_억원"].map(lambda x: f"{x:,.0f}억원")
    nh_show["비주택 신규수주"] = nh_show["비주택_신규수주_억원"].map(lambda x: f"{x:,.0f}억원")
    nh_show["비주택 비중"] = nh_show["비주택_비중_%"].map(lambda x: f"{x:.1f}%")
    st.dataframe(nh_show[["기간","전체 신규수주","비주택 신규수주","비주택 비중"]], hide_index=True, use_container_width=True)

    fig_nh = px.bar(nonhousing_total, x="기간", y=["비주택_신규수주_억원", "전체_신규수주_억원"], barmode="group",
                    title="전체 신규수주와 비주택 신규수주", labels={"value":"억원", "variable":"구분"})
    st.plotly_chart(fig_nh, use_container_width=True)

    st.markdown("""
    <div class="kolon-card"><b>먼저 확인되는 사실</b><br><br>
    2023~2025년 비주택 신규수주는 각각 약 <b>1.6조원 → 2.3조원 → 1.66조원</b>으로 전체 신규수주의 절반 안팎을 차지했습니다.
    2026년 상반기에도 전체 9,854억원 중 비주택이 <b>4,753억원(48.2%)</b>입니다.<br><br>
    따라서 비주택은 아직 작은 실험사업이 아니라 이미 건설 신규수주의 중요한 축입니다. 다음 질문은 <b>그 비주택 안에서 어떤 종류의 사업이 실제로 반복되고 있는가</b>입니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 2. 공개자료에서 개별 확인 가능한 비주택 프로젝트를 같은 기준으로 분류")
    filter_period = st.selectbox("기간 선택", ["전체", "2023", "2024", "2025", "2026 H1"], key="nh_period")
    project_view = nonhousing_projects.copy() if filter_period == "전체" else nonhousing_projects[nonhousing_projects["기간"]==filter_period].copy()
    project_view["금액"] = project_view["금액_억원"].map(lambda x: f"{x:,.0f}억원")
    st.dataframe(project_view[["기간","프로젝트","대분류","세부분류","금액","금액성격","근거"]], hide_index=True, use_container_width=True)

    st.warning("중요: 위 표는 '모든 비주택 신규수주 목록'이 아니라 공개자료에서 개별 식별 가능한 건입니다. 특히 사업보고서의 현재 계약액과 계약변경액은 신규수주액에 합산하지 않습니다. 전체 비주택 신규수주 총액과 개별 공개 프로젝트를 억지로 일치시키지 않습니다.")

    st.markdown("### 3. 왜 분류를 '하이테크 / 수처리'가 아니라 Value Chain으로 바꿨나?")
    st.markdown("""
    <div class="kolon-card">
    기존에는 <b>첨단산업시설</b>과 <b>수처리</b>를 별도 후보로 놓았습니다. 하지만 실제 프로젝트를 보면 둘이 반복적으로 연결됩니다.<br><br>
    • 삼성전자 평택 → 반도체 시설과 정수·폐수 인프라<br>
    • 머크 → 바이오 생산시설<br>
    • 도쿄일렉트론코리아 → 반도체 장비 연구시설<br>
    • 용인 반도체 산업단지 → 반도체 클러스터의 통합용수 공급<br><br>
    따라서 본 분석에서는 이를 <b>「첨단·산업시설 Value Chain」</b>으로 묶습니다. 즉 공장 건물만 시공하는 것이 아니라 <b>산업시설 시공 + 용수·폐수 등 생산 인프라</b>를 함께 볼 수 있는 성장축인지 검증합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 4. 2026년 상반기는 전체 비주택 수주 대비 '확인 가능한 최소 비중'까지 계산")
    a,b,c = st.columns(3)
    a.metric("2026 H1 비주택 신규수주", f"{nh26:,.0f}억원")
    b.metric("개별 확인 신규수주", f"{identified_26_total:,.0f}억원", f"{identified_26_coverage:.1f}% 확인")
    c.metric("개별 미공개/기타", f"{unclassified_26:,.0f}억원", "임의 분류하지 않음")

    fig_id = px.bar(identified_26, x="대분류", y="금액_억원", text="금액_억원",
                    title="2026 H1 공개자료로 직접 확인되는 비주택 신규수주 구성")
    fig_id.update_traces(texttemplate="%{text:,.0f}억원", textposition="outside")
    st.plotly_chart(fig_id, use_container_width=True)

    value26 = identified_26.loc[identified_26["대분류"]=="첨단·산업시설 Value Chain", "금액_억원"].sum()
    energy26 = identified_26.loc[identified_26["대분류"]=="에너지·신재생", "금액_억원"].sum()
    st.markdown(f"""
    <div class="kolon-card"><b>2026 H1에서 숫자로 확인되는 부분</b><br><br>
    공개된 개별 신규수주 중 <b>첨단·산업시설 Value Chain {value26:,.0f}억원</b>(용인 반도체 용수 1,265억원 + 금호타이어 제조공장 399억원),
    <b>에너지·신재생 {energy26:,.0f}억원</b>(울진 기성 풍력)이 확인됩니다.<br><br>
    두 범주 합계는 <b>{identified_26_total:,.0f}억원</b>으로 상반기 전체 비주택 신규수주 4,753억원의 <b>{identified_26_coverage:.1f}%</b>입니다.
    나머지 {unclassified_26:,.0f}억원은 공개된 전체 수치만으로 개별 프로젝트를 확정할 수 없어 특정 후보에 배분하지 않았습니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 5. 첨단·산업시설 Value Chain에 추가 근거가 있는가?")
    st.markdown("""
    <div class="kolon-card">
    <b>수주만 있는가?</b> → 아니다. 반도체·바이오·항공 MRO·제조시설 프로젝트가 여러 해에 걸쳐 반복됩니다.<br><br>
    <b>기술 연결이 있는가?</b> → 있다. 코오롱글로벌은 기존 저에너지 분리막 수처리 기술을 반도체 수처리로 확대하기 위한 R&D를 진행하고 있습니다.<br><br>
    <b>조직 연결이 있는가?</b> → 있다. 회사는 하이테크 관련 조직과 산업건설 수행역량을 강화해 왔습니다.<br><br>
    <b>그러면 무엇까지 말할 수 있나?</b> → 첨단·산업시설은 단순 시장 기대가 아니라 <b>반복되는 실제 프로젝트 + 수처리 기술 + 전담 수행역량</b>이 겹치는 영역이라고 볼 수 있습니다.
    다만 하이테크의 별도 매출과 영업이익률은 공시되지 않으므로 <b>가장 수익성이 높은 사업이라고 단정하지 않습니다.</b>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="kolon-note"><b>6번 탭 결론</b><br><br>
    비주택을 개별 사업명으로 흩어 보기보다 실제 프로젝트를 다시 묶어보면, <b>① 첨단·산업시설 Value Chain ② 공공 인프라 ③ 에너지·신재생</b>의 세 축으로 정리할 수 있습니다.<br><br>
    그중 첨단·산업시설 Value Chain은 반도체·바이오·MRO·제조시설과 용수·폐수 인프라가 반복적으로 나타나고, 회사의 수처리 R&D와도 연결됩니다.
    따라서 최종 탭에서는 '하이테크가 좋아 보인다'가 아니라 <b>실제 수주 반복성과 기존 기술의 결합 가능성</b>을 근거로 자원배분 방향을 제시합니다.
    </div>
    """, unsafe_allow_html=True)

with tab7:
    st.subheader("⑦ 검증 결과 → 자원배분 제언")
    st.write("이 탭에서는 새로운 사실을 만들지 않습니다. 4~6번 탭에서 확인한 숫자와 사업 특성을 자원배분 의사결정으로 연결합니다.")

    st.markdown("### 1. 제언보다 근거를 먼저")
    st.dataframe(allocation_logic, hide_index=True, use_container_width=True)

    st.markdown("### 2. 가장 먼저 강화할 연결: 첨단산업시설 × 수처리")
    st.markdown(f"""
    <div class="kolon-card">
    <b>① 숫자</b><br>
    2026년 상반기 비주택 신규수주 4,753억원 가운데 공개자료로 직접 확인되는 첨단·산업시설 Value Chain 신규수주는 최소 <b>{value26:,.0f}억원</b>입니다.<br><br>
    <b>② 반복성</b><br>
    삼성전자 평택, 머크 바이오, 대한항공 엔진정비공장, 도쿄일렉트론코리아 연구시설, 용인 반도체 용수공급, 금호타이어 제조공장 등 서로 다른 고객·산업에서 프로젝트가 확인됩니다.<br><br>
    <b>③ 기존 역량과의 연결</b><br>
    코오롱글로벌은 수처리 수행경험과 자체 기술을 보유하고 이를 반도체 수처리로 확장하고 있습니다. 따라서 완전히 새로운 분야에 진입하는 투자보다 <b>기존 환경기술을 첨단산업시설 수주에 결합</b>하는 방향입니다.<br><br>
    <b>→ 자원배분 제언</b><br>
    하이테크 전문인력, 산업시설 원가·공정관리 역량, 반도체 수처리 R&D, 기업고객 수주조직 간 협업에 우선적으로 성장자원을 배분합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 3. 나머지 축은 같은 방식으로 역할을 구분")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("""<div class="kolon-card"><b>공공 인프라</b><br><br><b>근거</b><br>철도·토목·공공 수처리 등 기존 수행기반<br><br><b>제언</b><br>외형 확대 자체보다 수익성 기준의 선별수주와 원가·공정관리 역량에 집중합니다.</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="kolon-card"><b>에너지·신재생</b><br><br><b>근거</b><br>바이오매스·풍력 프로젝트와 2026 H1 울진 기성 풍력 770억원 신규수주<br><br><b>제언</b><br>후속 개발 파이프라인과 사업성 검증, EPC 역량에 선택적으로 자원을 배분합니다.</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class="kolon-card"><b>레저·AM</b><br><br><b>근거</b><br>합병 이후 실제 매출·영업이익 기여와 운영수익 구조 확인<br><br><b>제언</b><br>운영효율화와 장기 위탁운영 계약을 통해 건설 변동성을 보완하는 축으로 육성합니다.</div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="kolon-note"><b>최종 결론</b><br><br>
    포트폴리오 다각화의 핵심을 단순히 <b>주택 비중 축소</b>로 보지 않습니다.
    이미 비주택이 신규수주의 절반 안팎을 차지하는 만큼, 앞으로는 <b>어떤 비주택 수주가 회사의 기존 기술과 결합해 반복 가능한 경쟁력이 되는지</b>가 중요합니다.<br><br>
    공개자료에서 가장 뚜렷하게 연결되는 흐름은 <b>첨단·산업시설 시공과 수처리 기술의 결합</b>입니다.
    따라서 이 영역에는 전문인력·R&D·기업고객 수주역량을 연결해 성장자원을 배분하고, 공공 인프라는 수익성 중심의 선별수주, 에너지·신재생은 프로젝트별 사업성 검증, 레저·AM은 운영수익 확대라는 서로 다른 역할로 관리하는 방향을 제언합니다.<br><br>
    단, 이는 공개자료로 확인 가능한 <b>수주 반복성·기술 연계성·사업모델</b>을 바탕으로 한 자원배분 방향이며, 사업별 영업이익률이 공시되지 않은 만큼 '첨단산업시설이 가장 수익성이 높다'는 의미는 아닙니다.
    </div>
    """, unsafe_allow_html=True)

    st.caption("핵심 원칙: 전체 비주택 신규수주 총액과 개별 공개 프로젝트를 구분하고, 신규수주·계약변경·현재 계약액을 섞지 않습니다. 확인되지 않은 프로젝트 금액은 특정 후보에 임의 배분하지 않습니다.")

# -----------------------------
# 출처 / 유의사항
# -----------------------------
st.divider()
with st.expander("데이터 출처 및 해석 유의사항"):
    st.markdown("""
    **기존 분석 출처**
    - 사용자가 제공한 2023·2024·2025 코오롱글로벌 사업보고서 및 공시자료
    - 2025 판매경로별 매출: 건설 2,307,978백만원, 상사 302,576백만원, 레저 76,035백만원, AM 4,586백만원
    - 건설 신규수주: 2023년 약 3.1조원, 2024년 약 4.2조원, 2025년 약 3.0조원
    - 비주택 신규수주: 2023년 약 1.6조원, 2024년 약 2.3조원, 2025년 약 1.7조원
    - 연말 수주잔고: 2023년 약 10.96조원, 2024년 약 11.66조원, 2025년 약 11.8조원

    **다각화 확장 분석 출처**
    - 2026년 1분기 공시 및 회사 실적발표: 신규수주 4,044억원, 레저·AM 합산 매출 649억원, 전년동기 대비 +344.5%, 영업이익 흑자전환
    - 회사 공개자료: 2024년 비주택 신규수주 2.3조원 이상, 하이테크 사업조직 신설 및 관련 전문인력 채용 확대
    - 2026년 1분기 회사 발표: 울진 기성 풍력단지 770억원 신규수주
    - 2026년 공시 R&D: 수처리 및 반도체 폐수 특정물질 처리기술 등 기술개발

    **해석 유의사항**
    - 상사를 '탈락'시킨다는 의미는 기존 사업의 축소·철수를 뜻하지 않습니다. 추가 성장자원 배분 후보군에서 우선순위를 낮춘다는 의미입니다.
    - 2025년 말 합병으로 레저·AM의 사업범위가 확대돼 2025년과 2026년의 단순 성장률 비교에는 한계가 있습니다.
    - 레저·AM은 회사 발표에서 합산 실적으로 제시되는 경우가 있어 개별 영업이익률을 임의로 분리하지 않습니다.
    - 산업·하이테크·환경·수처리·풍력은 건설부문 안에 포함되어 개별 영업이익률이 별도 공시되지 않으므로 수익성 우열을 단정하지 않습니다.
    - 신규수주와 회계 주석의 당기 계약액은 서로 다른 지표입니다.
    - 수주잔고는 미래 매출의 참고지표이며 계약변경·공정·원가·해지 등에 따라 실제 매출과 차이가 날 수 있습니다.
    """)

st.caption("KOLON Global Financial Insight · 개인 재무분석 프로젝트")
