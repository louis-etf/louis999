# Streamlit Cloud 部署指南

這個文件提供了如何將 ETF 配息分析工具部署到 Streamlit Cloud 的詳細步驟。

## 前置準備

1. 一個 GitHub 帳號
2. 一個 Streamlit Cloud 帳號 (可以使用 GitHub 帳號登入)

## 部署步驟

### 1. 在 GitHub 上創建新倉庫

1. 登入您的 GitHub 帳號
2. 點擊右上角的 "+" 圖標，選擇 "New repository"
3. 倉庫名稱填寫 "etf-analyzer"
4. 選擇 "Public" (公開)
5. 不要初始化倉庫 (不要勾選 "Add a README file")
6. 點擊 "Create repository"

### 2. 上傳文件到 GitHub

**方法一：使用 GitHub 網頁界面**

1. 在新創建的倉庫頁面，點擊 "uploading an existing file" 連結
2. 將解壓後的文件拖拽到上傳區域：
   - app.py
   - requirements.txt
   - README.md
   - data/ 目錄下的所有文件
3. 點擊 "Commit changes"

**方法二：使用 Git 命令行**

如果您熟悉 Git 命令行，可以按照以下步驟操作：

```bash
# 克隆倉庫
git clone https://github.com/您的用戶名/etf-analyzer.git

# 進入倉庫目錄
cd etf-analyzer

# 解壓並複製文件
# 將解壓後的文件複製到此目錄

# 添加文件
git add .

# 提交更改
git commit -m "Initial commit"

# 推送到 GitHub
git push origin main
```

### 3. 在 Streamlit Cloud 上部署

1. 訪問 [Streamlit Cloud](https://streamlit.io/cloud)
2. 使用您的 GitHub 帳號登入
3. 點擊 "New app" 按鈕
4. 在 "Repository" 下拉菜單中選擇 "您的用戶名/etf-analyzer"
5. 在 "Branch" 中選擇 "main"
6. 在 "Main file path" 中輸入 "app.py"
7. 點擊 "Deploy!" 按鈕

部署過程可能需要幾分鐘時間。完成後，您將獲得一個可以訪問的 URL，格式類似：
`https://您的用戶名-etf-analyzer-app-xxxxx.streamlit.app`

### 4. 驗證部署

1. 訪問 Streamlit Cloud 提供的 URL
2. 確認應用程序正常運行
3. 測試各項功能是否正常工作

## 故障排除

如果部署過程中遇到問題：

1. 檢查 GitHub 倉庫中的文件結構是否正確
2. 確認 requirements.txt 文件包含所有必要的依賴
3. 查看 Streamlit Cloud 的部署日誌，尋找錯誤信息
4. 如果應用無法啟動，可能是因為依賴問題，嘗試更新 requirements.txt

## 更新應用

當您需要更新應用時，只需更新 GitHub 倉庫中的文件，Streamlit Cloud 將自動重新部署。
