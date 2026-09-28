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
→ ④ 매출 인식 후 청구 전 단계의 미청구공사는 어디에서 증가했는가
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "① 사업 포트폴리오",
    "② 신규수주 → 수주잔고 → 매출",
    "③ 매출 → 청구 → 회수"
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
# 출처 / 유의사항
# -----------------------------
st.divider()
with st.expander("데이터 출처 및 해석 유의사항"):
    st.markdown("""
    **출처**
    - 사용자가 제공한 2023·2024·2025 ㈜코오롱 사업보고서 내 코오롱글로벌 관련 공시
    - 2025 판매경로별 매출: 건설 2,307,978백만원, 상사 302,576백만원,
      레저 76,035백만원, AM 4,586백만원
    - 건설 신규수주: 2023년 약 3.1조원, 2024년 약 4.2조원, 2025년 약 3.0조원
    - 비주택 신규수주: 2023년 약 1.6조원, 2024년 약 2.3조원, 2025년 약 1.7조원
    - 연말 수주잔고: 2023년 약 10.96조원, 2024년 약 11.66조원, 2025년 약 11.8조원
    - 주요 건설계약 합계:
      2023 미청구공사 78,962백만원 / 공사미수금 96,492백만원,
      2024 86,560백만원 / 154,741백만원,
      2025 123,523백만원 / 153,611백만원

    **유의사항**
    - 이 도구는 공시자료를 구조화해 관계를 빠르게 파악하기 위한 개인 분석 프로젝트입니다.
    - 주요계약 표의 미청구공사·공사미수금 합계는 회사 전체 계정잔액과 동일하지 않습니다.
    - 전체 진행 중 건설계약 미청구공사: 2024년 299,432백만원 / 2025년 298,287백만원
    - 2025년 전체 미청구공사 부문별 잔액: 국내토목 72,535 / 국내건축 30,185 / 국내플랜트 16,152 / 국내주택 147,748 / 국내환경 8,701 / 해외도급 22,966백만원
    - 신규수주와 회계 주석의 당기 계약액은 서로 다른 지표입니다. 당기 계약액에는 신규수주와 계약변경에 따른 도급액 변동 등이 포함됩니다.
    - 수주잔고는 향후 매출의 참고지표이며, 계약 변경·공정·원가·해지 등에 따라 실제 매출 인식 시점과 금액이 달라질 수 있습니다.
    - 특정 수치만으로 부실·위험 여부를 단정하지 않습니다.
    """)

st.caption("KOLON Global Financial Insight · 개인 재무분석 프로젝트")
