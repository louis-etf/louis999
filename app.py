import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import datetime
import time
import requests
import yfinance as yf
from bs4 import BeautifulSoup
import schedule
import threading

#########################################
# 多重編碼讀取 CSV 函式
#########################################
def try_read_csv(file_path, **kwargs):
    encodings = ['cp950', 'big5', 'utf-8', 'latin1']
    last_exception = None
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, **kwargs)
            return df
        except Exception as e:
            last_exception = e
    raise last_exception

#########################################
# 全局初始化 Session State
#########################################
if 'current_age' not in st.session_state:
    st.session_state.current_age = 30
if 'retirement_age' not in st.session_state:
    st.session_state.retirement_age = 65
if 'initial_investment' not in st.session_state:
    st.session_state.initial_investment = 50000
if 'monthly_savings' not in st.session_state:
    st.session_state.monthly_savings = 4000
if 'expected_return' not in st.session_state:
    st.session_state.expected_return = 5.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'selected_etfs' not in st.session_state:
    st.session_state.selected_etfs = {}

#########################################
# 設置頁面配置與自訂 CSS 樣式
#########################################
st.set_page_config(
    page_title="投資理財工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(r"""
<style>
[data-testid="stToolbar"] { visibility: hidden; }
.stApp {
    background: #2C2C2C;
    color: #EEEEEE;
}
h1, h2, h3 {
    color: #87CEEB;
    font-weight: 600;
}
.metric-container, .stCard {
    background: #3A3A3A;
    border: 1px solid #555555;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.5);
}
.metric-label {
    color: #CCCCCC;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}
.metric-value {
    color: #87CEEB;
    font-size: 1.5rem;
    font-weight: 600;
}
.stNumberInput > div > div > input {
    background: #3A3A3A;
    border: 1px solid #555555;
    color: #EEEEEE;
    border-radius: 8px;
}
.chart-container {
    background: #3A3A3A;
    border: 1px solid #555555;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
}
.analysis-section {
    margin-top: 2rem;
    padding: 1rem;
    background: #3A3A3A;
    border-radius: 8px;
    border: 1px solid #555555;
}
.etf-info {
    padding: 1rem;
    background: #3A3A3A;
    border-radius: 8px;
    border: 1px solid #555555;
    margin-bottom: 0.5rem;
}
.etf-code {
    color: #87CEEB;
    font-weight: 600;
    font-size: 1.1rem;
}
.etf-name {
    color: #AAAAAA;
    font-size: 0.9rem;
    margin-top: 0.3rem;
}
/* 斗內按鈕樣式 */
.donate-button {
    display: block;
    background-color: #FF5722;
    color: white;
    text-align: center;
    padding: 10px 15px;
    border-radius: 8px;
    margin: 20px auto;
    font-weight: bold;
    text-decoration: none;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}
.donate-button:hover {
    background-color: #16a085;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

#########################################
# 存股計算器相關函式
#########################################
def plot_investment_growth(years, values):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=values,
        mode='lines+markers',
        name='累積金額',
        line=dict(color='#87CEEB', width=2),
        marker=dict(size=8),
        hovertemplate="年份: %{x}<br>累積金額: NT$%{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text='累積金額成長曲線', font=dict(size=18, color='#87CEEB'), y=0.95),
        plot_bgcolor='#3A3A3A',
        paper_bgcolor='#3A3A3A',
        font=dict(color='#EEEEEE', size=12),
        xaxis=dict(title='年份', gridcolor='#555555', zerolinecolor='#555555', tickfont=dict(size=12)),
        yaxis=dict(title='累積金額 (NT$)', gridcolor='#555555', zerolinecolor='#555555', tickformat=',d', tickfont=dict(size=12)),
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig

def show_investment_calculator():
    st.markdown("<h1>存股計算</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3>投資參數設定</h3>", unsafe_allow_html=True)
        current_age = st.number_input("目前年齡", min_value=18, max_value=100, value=st.session_state.current_age, step=1)
        retirement_age = st.number_input("預計退休年齡", min_value=current_age, max_value=100, value=st.session_state.retirement_age, step=1)
        initial_investment = st.number_input("初始投資金額 (NT$)", min_value=0, value=st.session_state.initial_investment, step=10000)
        monthly_savings = st.number_input("每月投入金額 (NT$)", min_value=0, value=st.session_state.monthly_savings, step=1000)
        expected_return = st.number_input("預期年化報酬率 (%)", min_value=0.0, max_value=20.0, value=st.session_state.expected_return, step=0.5)
        
        st.session_state.current_age = current_age
        st.session_state.retirement_age = retirement_age
        st.session_state.initial_investment = initial_investment
        st.session_state.monthly_savings = monthly_savings
        st.session_state.expected_return = expected_return
    
    years = retirement_age - current_age
    monthly_return = (1 + expected_return/100) ** (1/12) - 1
    
    values = [initial_investment]
    current_value = initial_investment
    for i in range(1, years * 12 + 1):
        current_value = current_value * (1 + monthly_return) + monthly_savings
        if i % 12 == 0:
            values.append(current_value)
    
    with col2:
        st.markdown("<h3>投資成長預測</h3>", unsafe_allow_html=True)
        final_amount = values[-1]
        monthly_income = final_amount * (expected_return/100/12)
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">退休時累積金額</div>
            <div class="metric-value">NT${final_amount:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">預估每月被動收入</div>
            <div class="metric-value">NT${monthly_income:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3>投資成長曲線</h3>", unsafe_allow_html=True)
    year_labels = list(range(current_age, retirement_age + 1))
    fig = plot_investment_growth(year_labels, values)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<h3>投資建議</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div class="analysis-section">
        <p>根據您的投資計劃，以下是一些建議：</p>
        <ul>
            <li>定期檢視您的投資組合，確保符合預期報酬率</li>
            <li>考慮通貨膨脹因素，適時調整每月投入金額</li>
            <li>分散投資於不同類型的ETF，降低風險</li>
            <li>利用ETF配息分析器頁面，選擇適合的ETF進行投資</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

#########################################
# ETF 配息分析器核心類別與函式
#########################################
class ClassifiedDividendAnalyzer:
    def __init__(self):
        self.data_path = os.path.dirname(os.path.abspath(__file__))
        unified_file = os.path.join(self.data_path, 'etf_dividend_022.csv')
        try:
            self.price_data = try_read_csv(unified_file)
            self.price_data['股票代號'] = self.price_data['股票代號'].astype(str).str.strip()
            self.price_data['股票代號'] = self.price_data['股票代號'].apply(self.format_etf_code)
            self.price_data['收盤價'] = pd.to_numeric(self.price_data['收盤價'], errors='coerce')
            self.price_data = self.price_data.dropna(subset=['收盤價'])
        except Exception as e:
            st.error("讀取價格數據時發生錯誤: " + str(e))
            self.price_data = None
        try:
            self.data = try_read_csv(unified_file)
            self.data['股票代號'] = self.data['股票代號'].astype(str).str.strip()
            self.data['股票代號'] = self.data['股票代號'].apply(self.format_etf_code)
            self.data['除息日'] = pd.to_datetime(self.data['除息日'], errors='coerce')
            self.data = self.data.dropna(subset=['除息日'])
            self.data['月份'] = self.data['除息日'].dt.month
            self.classify_dividends()
        except Exception as e:
            st.error("讀取配息數據時發生錯誤: " + str(e))
            self.data = None

    def format_etf_code(self, code):
        code = str(code).strip()
        if len(code) < 5 and 'B' not in code:
            code = code.zfill(5)
        return code

    def classify_dividends(self):
        if self.data is None:
            return
        self.data['發放標籤'] = '不定期'
        for etf_code in self.data['股票代號'].unique():
            etf_data = self.data[self.data['股票代號'] == etf_code]
            dividend_count = len(etf_data)
            months = sorted(etf_data['月份'].unique())
            if dividend_count >= 12:
                self.data.loc[self.data['股票代號'] == etf_code, '發放標籤'] = '月月配'
            elif dividend_count == 4:
                if months == [1, 4, 7, 10]:
                    self.data.loc[self.data['股票代號'] == etf_code, '發放標籤'] = '季配息(1,4,7,10月)'
                elif months == [2, 5, 8, 11]:
                    self.data.loc[self.data['股票代號'] == etf_code, '發放標籤'] = '季配息(2,5,8,11月)'
                elif months == [3, 6, 9, 12]:
                    self.data.loc[self.data['股票代號'] == etf_code, '發放標籤'] = '季配息(3,6,9,12月)'
            elif dividend_count == 2:
                self.data.loc[self.data['股票代號'] == etf_code, '發放標籤'] = '半年配'
            elif dividend_count == 1:
                self.data.loc[self.data['股票代號'] == etf_code, '發放標籤'] = '年配'
        if '每單位配發金額(元)' in self.data.columns:
            self.data['每千單位配發金額'] = self.data['每單位配發金額(元)'] * 1000
        else:
            st.error("CSV 缺少「每單位配發金額(元)」欄位，請確認。")

    def get_etfs_by_dividend_frequency(self):
        if self.data is None:
            return {}
        freq_map = {}
        for freq in self.data['發放標籤'].unique():
            freq_map[freq] = sorted(self.data.loc[self.data['發放標籤'] == freq, '股票代號'].unique())
        return freq_map

    def get_all_etfs(self):
        if self.data is not None and self.price_data is not None:
            data_codes = set(self.data['股票代號'].astype(str))
            price_codes = set(self.price_data['股票代號'].astype(str))
            valid_etfs = data_codes.intersection(price_codes)
            return sorted(list(valid_etfs))
        return []

    def get_etf_name(self, etf_code):
        etf_code = self.format_etf_code(etf_code)
        if self.price_data is not None and etf_code in self.price_data['股票代號'].values:
            return self.price_data[self.price_data['股票代號'] == etf_code]['股票名稱'].iloc[0]
        elif self.data is not None:
            mask = self.data['股票代號'] == etf_code
            if mask.any():
                return self.data[mask]['股票名稱'].iloc[0]
        return f"ETF {etf_code}"

    def get_etf_price(self, etf_code):
        etf_code = self.format_etf_code(etf_code)
        if self.price_data is not None and etf_code in self.price_data['股票代號'].values:
            return float(self.price_data[self.price_data['股票代號'] == etf_code]['收盤價'].iloc[0])
        return None

    def calculate_investment_cost(self, portfolio):
        total_cost = 0
        details = []
        for etf, quantity in portfolio.items():
            price = self.get_etf_price(etf)
            if price is not None:
                cost = price * quantity
                details.append({
                    "ETF代號": etf,
                    "ETF名稱": self.get_etf_name(etf),
                    "購買數量（千股）": f"{quantity/1000:.1f}",
                    "實際股數": f"{quantity:,}",
                    "收盤價": f"{price:.2f}",
                    "投資金額": f"NT${cost:,.0f}"
                })
                total_cost += cost
        return total_cost, details

    def get_monthly_dividends(self, portfolio):
        if self.data is None or not portfolio:
            return None
        filtered_data = self.data[self.data['股票代號'].isin(portfolio.keys())].copy()
        for etf, quantity in portfolio.items():
            mask = filtered_data['股票代號'] == etf
            if '每千單位配發金額' in filtered_data.columns:
                filtered_data.loc[mask, '每千單位配發金額'] *= quantity / 1000
        return filtered_data

#########################################
# 投資組合管理與指標展示相關函式
#########################################
def update_portfolio():
    new_portfolio = {}
    for etf in st.session_state.selected_etfs:
        quantity = st.session_state.get(f"qty_{etf}", 0)
        actual_quantity = int(quantity * 1000)
        if actual_quantity > 0:
            new_portfolio[etf] = actual_quantity
    st.session_state.portfolio = new_portfolio

def display_portfolio_metrics(analyzer, portfolio_data, total_cost):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
<div class="metric-container">
    <div class="metric-label">總投資金額</div>
    <div class="metric-value">NT${total_cost:,.0f}</div>
</div>
""", unsafe_allow_html=True)
    annual_dividends = 0
    filtered_data = analyzer.get_monthly_dividends(st.session_state.portfolio)
    if filtered_data is not None and not filtered_data.empty:
        annual_dividends = filtered_data['每千單位配發金額'].sum()
    with col2:
        st.markdown(f"""
<div class="metric-container">
    <div class="metric-label">預估年配息</div>
    <div class="metric-value">NT${annual_dividends:,.0f}</div>
</div>
""", unsafe_allow_html=True)
    with col3:
        dividend_yield = (annual_dividends / total_cost * 100) if total_cost > 0 else 0
        st.markdown(f"""
<div class="metric-container">
    <div class="metric-label">平均報酬率</div>
    <div class="metric-value">{dividend_yield:.2f}%</div>
</div>
""", unsafe_allow_html=True)

def plot_monthly_dividends(filtered_data):
    if filtered_data is None or filtered_data.empty:
        st.warning("配息資料為空，無法繪製圖表。")
        return None

    pivot_data = filtered_data.pivot_table(
        index='月份',
        columns='股票代號',
        values='每千單位配發金額',
        aggfunc='sum',
        fill_value=0
    )
    monthly_totals = pivot_data.sum(axis=1)
    annual_total = monthly_totals.sum()
    monthly_average = annual_total / 12 if annual_total > 0 else 0

    fig = go.Figure()
    colors = ['#87CEEB', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6',
              '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b']

    for idx, etf_code in enumerate(pivot_data.columns):
        hover_str = f"ETF: {etf_code}<br>月份: %{{x}}月<br>配息: NT$%{{y:,.0f}}<extra></extra>"
        fig.add_trace(go.Bar(
            x=pivot_data.index,
            y=pivot_data[etf_code],
            name=etf_code,
            marker_color=colors[idx % len(colors)],
            hovertemplate=hover_str
        ))

    fig.add_trace(go.Scatter(
        name='月平均',
        x=pivot_data.index,
        y=[monthly_average]*len(pivot_data.index),
        mode='lines',
        line=dict(color='#16a085', width=2, dash='dash'),
        hovertemplate="月平均: NT$%{y:,.0f}<extra></extra>"
    ))

    fig.add_annotation(
        x=-0.5,
        y=monthly_average,
        text=f'月平均: NT${monthly_average:,.0f}',
        showarrow=False,
        xanchor='right',
        font=dict(size=16, color='#16a085'),
        xref='x',
        yref='y'
    )

    title_text = f"月度配息分布 (年配息總額: NT${annual_total:,.0f}, 平均每月: NT${monthly_average:,.0f})"
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=24, color='#87CEEB'), y=0.95),
        barmode='stack',
        plot_bgcolor='#3A3A3A',
        paper_bgcolor='#3A3A3A',
        font=dict(color='#EEEEEE', size=18),
        showlegend=True,
        legend=dict(
            bgcolor='#3A3A3A',
            bordercolor='#555555',
            borderwidth=1,
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.1,
            font=dict(size=16)
        ),
        xaxis=dict(
            title='月份',
            gridcolor='#555555',
            zerolinecolor='#555555',
            tickmode='array',
            ticktext=[f'{i}月' for i in range(1, 13)],
            tickvals=list(range(1, 13)),
            tickfont=dict(size=16),
            range=[-0.8, 12.5]
        ),
        yaxis=dict(
            title='配息金額 (NT$)',
            gridcolor='#555555',
            zerolinecolor='#555555',
            tickformat=',d',
            tickfont=dict(size=16)
        ),
        height=700,
        margin=dict(l=150, r=150, t=120, b=50)
    )

    for i, total in enumerate(monthly_totals):
        fig.add_annotation(
            x=pivot_data.index[i],
            y=total,
            text=f"NT${total:,.0f}",
            showarrow=False,
            yshift=10,
            font=dict(size=14, color='#EEEEEE')
        )

    return fig

def create_portfolio_summary_chart(portfolio_data):
    values = portfolio_data['投資金額'].str.replace('NT$', '').str.replace(',', '').astype(float)
    labels = [f"{code}<br>{name}" for code, name in zip(portfolio_data['ETF代號'], portfolio_data['ETF名稱'])]
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=['#87CEEB', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6',
                            '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b']),
        textinfo='percent',
        textfont=dict(size=14),
        hovertemplate="ETF: %{label}<br>金額: NT$%{value:,.0f}<br>佔比: %{percent}<extra></extra>"
    ))
    fig.update_layout(
        title=dict(text='投資組合配置', font=dict(size=18, color='#87CEEB'), y=0.95),
        plot_bgcolor='#3A3A3A',
        paper_bgcolor='#3A3A3A',
        font=dict(color='#EEEEEE', size=12),
        showlegend=True,
        legend=dict(
            bgcolor='#3A3A3A',
            bordercolor='#555555',
            borderwidth=1,
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.1,
            font=dict(size=12)
        ),
        height=350,
        margin=dict(l=20, r=120, t=50, b=20)
    )
    return fig

#########################################
# ETF 配息分析器頁面
#########################################
def show_analyzer():
    st.markdown(r"""
<div class="page-header">
    <h1>ETF配息分析器</h1>
</div>
""", unsafe_allow_html=True)
    analyzer = ClassifiedDividendAnalyzer()
    if analyzer.data is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(r"""
<div class="search-section">
    <h3>搜尋與添加ETF</h3>
</div>
""", unsafe_allow_html=True)
            search_method = st.radio(
                "選擇搜尋方式",
                ["配息類型篩選", "搜尋ETF"],
                horizontal=True,
                key="search_method"
            )
            if search_method == "配息類型篩選":
                frequency_groups = analyzer.get_etfs_by_dividend_frequency()
                if not frequency_groups:
                    st.warning("目前無法取得任何ETF配息頻率資料，請確認CSV檔案是否正確。")
                else:
                    dividend_frequency = st.selectbox("選擇配息頻率", options=list(frequency_groups.keys()))
                    if dividend_frequency:
                        filtered_etfs = frequency_groups[dividend_frequency]
                        if filtered_etfs:
                            temp_selected_etf = st.selectbox("選擇ETF", filtered_etfs,
                                                             format_func=lambda x: f"{x} ({analyzer.get_etf_name(x)})")
                            price = analyzer.get_etf_price(temp_selected_etf)
                            if price:
                                st.markdown(r"""
<div class="etf-info">
    <p>當前價格: NT${:.2f}</p>
</div>
""".format(price), unsafe_allow_html=True)
                            if st.button("➕ 添加到投資組合", key="btn_add_etf_search"):
                                if temp_selected_etf not in st.session_state.selected_etfs:
                                    st.session_state.selected_etfs[temp_selected_etf] = 0
                                    st.success(f"已添加 {temp_selected_etf} 到投資組合")
                                else:
                                    st.warning("此ETF已在投資組合中")
                        else:
                            st.info("沒有找到符合條件的ETF")
            elif search_method == "搜尋ETF":
                all_etfs = analyzer.get_all_etfs()
                if not all_etfs:
                    st.warning("目前無法取得任何ETF資料，請確認CSV檔案是否正確。")
                else:
                    search_keyword = st.text_input("輸入ETF代號或關鍵字", "")
                    if search_keyword.strip():
                        kw = search_keyword.strip().upper()
                        matched_etfs = [etf for etf in all_etfs if kw in etf or kw in analyzer.get_etf_name(etf).upper()]
                    else:
                        matched_etfs = all_etfs
                    if matched_etfs:
                        temp_selected_etf = st.selectbox(
                            "選擇ETF",
                            matched_etfs,
                            format_func=lambda x: f"{x} ({analyzer.get_etf_name(x)})"
                        )
                        price = analyzer.get_etf_price(temp_selected_etf)
                        if price:
                            st.markdown(r"""
<div class="etf-info">
    <p>當前價格: NT${:.2f}</p>
</div>
""".format(price), unsafe_allow_html=True)
                        if st.button("➕ 添加到投資組合", key="btn_add_etf_search2"):
                            if temp_selected_etf not in st.session_state.selected_etfs:
                                st.session_state.selected_etfs[temp_selected_etf] = 0
                                st.success(f"已添加 {temp_selected_etf} 到投資組合")
                            else:
                                st.warning("此ETF已在投資組合中")
                    else:
                        st.info("沒有符合關鍵字的ETF。")
        with col2:
            st.markdown(r"""
<div class="portfolio-section">
    <h3>投資組合管理</h3>
</div>
""", unsafe_allow_html=True)
            if st.session_state.selected_etfs:
                for etf in list(st.session_state.selected_etfs.keys()):
                    with st.container():
                        col_info, col_qty, col_remove = st.columns([2, 1, 0.5])
                        with col_info:
                            st.markdown(f"""
<div class="etf-info">
    <div class="etf-code">{etf}</div>
    <div class="etf-name">{analyzer.get_etf_name(etf)}</div>
</div>
""", unsafe_allow_html=True)
                        with col_qty:
                            default_value = st.session_state.portfolio.get(etf, 0) / 1000
                            st.number_input("數量(千股)", min_value=0.0, value=float(default_value),
                                            step=0.1, format="%.1f", key=f"qty_{etf}", on_change=update_portfolio)
                        with col_remove:
                            if st.button("🗑️", key=f"remove_{etf}"):
                                del st.session_state.selected_etfs[etf]
            else:
                st.info("尚未添加任何ETF到投資組合")
        
        if st.session_state.portfolio:
            st.markdown("---")
            st.markdown(r"""
<div class="analysis-section">
    <h2>投資組合分析</h2>
</div>
""", unsafe_allow_html=True)
            total_cost, portfolio_data = analyzer.calculate_investment_cost(st.session_state.portfolio)
            if portfolio_data:
                display_portfolio_metrics(analyzer, portfolio_data, total_cost)
                filtered_data = analyzer.get_monthly_dividends(st.session_state.portfolio)
                if filtered_data is not None and not filtered_data.empty:
                    st.markdown("<h3>各ETF月度配息明細</h3>", unsafe_allow_html=True)
                    fig = plot_monthly_dividends(filtered_data)
                    if fig is not None:
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(r"""
<div class="details-section">
    <h3>投資組合詳細資訊</h3>
</div>
""", unsafe_allow_html=True)
                    st.table(pd.DataFrame(portfolio_data))
                with col2:
                    st.plotly_chart(create_portfolio_summary_chart(pd.DataFrame(portfolio_data)),
                                      use_container_width=True, config={'displayModeBar': False})
    else:
        st.error("讀取配息資料失敗，請確認CSV檔案是否正確。")

#########################################
# 側邊欄：只保留捐款按鈕
#########################################
def show_sidebar():
    st.sidebar.markdown("<h2>投資理財工具</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("這是一個幫助您分析ETF配息與存股投資的工具。")
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <a href="https://pay.soundon.fm/podcasts/48c567ce-cca7-4442-b327-ba611ad307d2" target="_blank" class="donate-button">
        ❤️ 支持創作者
    </a>
    """, unsafe_allow_html=True)

#########################################
# 主程式入口：使用 st.tabs 呈現兩大功能
#########################################
def main():
    show_sidebar()
    tabs = st.tabs(["存股計算", "ETF配息分析器"])
    with tabs[0]:
        show_investment_calculator()
    with tabs[1]:
        show_analyzer()

#########################################
# 定時任務與 ETF 數據更新功能
#########################################
def start_scheduler():
    scheduler_thread = threading.Thread(target=schedule_update)
    scheduler_thread.daemon = True
    scheduler_thread.start()

def schedule_update():
    schedule.every().day.at("02:00").do(update_etf_data)
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    csv_path = os.path.join(data_dir, 'etf_dividend_data.csv')
    if not os.path.exists(csv_path):
        update_etf_data()
    while True:
        schedule.run_pending()
        time.sleep(60)

def update_etf_data():
    try:
        print(f"開始更新ETF數據: {datetime.datetime.now()}")
        etf_list = fetch_etf_list_from_twse()
        if not etf_list:
            print("無法獲取ETF列表，使用默認列表")
            etf_list = ['0050', '0056', '0057', '00878', '00881', '00891', '00892', '00896', '00713']
        df = fetch_etf_data_from_yahoo(etf_list)
        if df.empty:
            print("爬蟲獲取數據失敗，使用示例數據")
            df = create_sample_data()
        if not df.empty:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            os.makedirs(data_dir, exist_ok=True)
            csv_path = os.path.join(data_dir, 'etf_dividend_data.csv')
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"ETF數據已更新並保存到 {csv_path}")
            with open(os.path.join(data_dir, 'last_update.txt'), 'w') as f:
                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        else:
            print("獲取的ETF數據為空")
    except Exception as e:
        print(f"更新ETF數據時出錯: {str(e)}")

#########################################
# 爬蟲功能：從Yahoo Finance獲取ETF數據
#########################################
def fetch_etf_data_from_yahoo(etf_list):
    result_data = []
    for etf_code in etf_list:
        try:
            if etf_code.isdigit() or (len(etf_code) >= 4 and etf_code[:4].isdigit()):
                yahoo_code = f"{etf_code}.TW"
            else:
                yahoo_code = etf_code
            etf = yf.Ticker(yahoo_code)
            info = etf.info
            hist = etf.history(period="1d")
            if not hist.empty:
                close_price = hist['Close'].iloc[-1]
                dividends = etf.dividends
                now = datetime.datetime.now()
                recent_year = now - datetime.timedelta(days=365)
                if not dividends.empty:
                    dividend_dates = [d.to_pydatetime().replace(tzinfo=None) for d in dividends.index]
                    recent_dividends = dividends[[d >= recent_year for d in dividend_dates]]
                    annual_dividend = recent_dividends.sum()
                    avg_dividend = annual_dividend / len(recent_dividends) if len(recent_dividends) > 0 else 0
                else:
                    annual_dividend = 0
                    avg_dividend = 0
                record = {
                    '股票代號': etf_code,
                    '股票名稱': info.get('shortName', f'ETF {etf_code}'),
                    '收盤價': close_price,
                    '每單位配發金額(元)': avg_dividend,
                    '除息日': now.strftime('%Y-%m-%d')
                }
                result_data.append(record)
                print(f"成功獲取 {etf_code} 數據")
            else:
                print(f"無法獲取 {etf_code} 的價格數據")
        except Exception as e:
            print(f"獲取 {etf_code} 數據時出錯: {str(e)}")
    if result_data:
        return pd.DataFrame(result_data)
    else:
        return pd.DataFrame()

#########################################
# 爬蟲功能：從台灣證券交易所獲取ETF列表
#########################################
def fetch_etf_list_from_twse():
    try:
        url = "https://www.twse.com.tw/zh/page/ETF/list.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        etf_list = []
        tables = soup.find_all('table')
        if tables:
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        etf_code = cols[0].text.strip()
                        if etf_code and etf_code.isdigit():
                            etf_list.append(etf_code)
        return etf_list
    except Exception as e:
        print(f"從證交所獲取ETF列表時出錯: {str(e)}")
        return []

#########################################
# 創建示例數據（當爬蟲失敗時使用）
#########################################
def create_sample_data():
    sample_data = [
        {'股票代號': '0050', '股票名稱': '元大台灣50', '收盤價': 142.50, '每單位配發金額(元)': 0.45, '除息日': '2025-03-15'},
        {'股票代號': '0056', '股票名稱': '元大高股息', '收盤價': 35.20, '每單位配發金額(元)': 0.18, '除息日': '2025-03-10'},
        {'股票代號': '00878', '股票名稱': '國泰永續高股息', '收盤價': 20.15, '每單位配發金額(元)': 0.12, '除息日': '2025-02-20'},
        {'股票代號': '00881', '股票名稱': '國泰台灣5G+', '收盤價': 18.75, '每單位配發金額(元)': 0.08, '除息日': '2025-01-15'},
        {'股票代號': '00891', '股票名稱': '中信關鍵半導體', '收盤價': 22.30, '每單位配發金額(元)': 0.10, '除息日': '2025-03-05'},
        {'股票代號': '00892', '股票名稱': '富邦台灣半導體', '收盤價': 25.40, '每單位配發金額(元)': 0.11, '除息日': '2025-02-10'},
        {'股票代號': '00896', '股票名稱': '中信綠能電動車', '收盤價': 16.85, '每單位配發金額(元)': 0.07, '除息日': '2025-01-25'},
        {'股票代號': '00713', '股票名稱': '元大台灣高息低波', '收盤價': 28.90, '每單位配發金額(元)': 0.15, '除息日': '2025-03-20'},
        {'股票代號': '00929', '股票名稱': '復華台灣科技優息', '收盤價': 19.75, '每單位配發金額(元)': 0.09, '除息日': '2025-02-15'}
    ]
    return pd.DataFrame(sample_data)

#########################################
# 主程式入口
#########################################
if __name__ == "__main__":
    start_scheduler()
    main()
