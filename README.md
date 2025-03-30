# ETF配息分析工具

這是一個使用Streamlit開發的ETF配息分析工具，幫助投資者分析ETF配息情況和規劃投資策略。

## 功能特點

1. **ETF配息分析**：
   - 按配息頻率篩選ETF
   - 搜尋特定ETF
   - 建立個人投資組合
   - 分析投資組合的配息分布和報酬率

2. **存股計算**：
   - 設定投資參數（初始投資、每月投入、預期報酬率等）
   - 計算退休時累積金額和被動收入
   - 視覺化投資成長曲線

3. **自動數據更新**：
   - 每日自動從Yahoo Finance和台灣證交所爬取最新ETF數據
   - 顯示數據最後更新時間

## 安裝與運行

### 本地運行

1. 克隆此倉庫：
   ```
   git clone https://github.com/yourusername/etf-analyzer.git
   cd etf-analyzer
   ```

2. 安裝依賴：
   ```
   pip install -r requirements.txt
   ```

3. 運行應用：
   ```
   streamlit run app.py
   ```

### Streamlit Cloud部署

1. Fork此倉庫到您的GitHub帳戶
2. 登入[Streamlit Cloud](https://streamlit.io/cloud)
3. 點擊"New app"並選擇您fork的倉庫
4. 設置主文件為`app.py`
5. 部署完成後，您可以通過Streamlit Cloud提供的URL訪問應用

## 數據來源

- 台灣證券交易所
- Yahoo Finance

## 支持創作者

如果您覺得這個工具有幫助，可以通過側邊欄的"支持創作者"按鈕進行斗內。

## 注意事項

- 本工具僅供參考，不構成投資建議
- 投資有風險，決策需謹慎
- 數據每日自動更新一次，更新時間為凌晨2點

## 授權

MIT License
