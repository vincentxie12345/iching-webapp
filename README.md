# 🔮 易經占卜 Web APP

手機友善的易經占卜系統，使用 Streamlit 建立。

## 📱 功能

- **A1 默禱**：心中默想問題，系統隨機起卦
- **A2 提問**：輸入問題，系統隨機起卦
- **A3 問卷**：回答六個評估問題，根據回答起卦
- **A4 Agent**：（開發中）AI 輔助分析起卦

## 🚀 本地執行

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定 API Key

複製 `.streamlit/secrets.toml.example` 為 `.streamlit/secrets.toml`：

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

編輯 `secrets.toml`，填入您的 API Key：

```toml
GEMINI_API_KEY = "your-gemini-api-key"
# 或
ANTHROPIC_API_KEY = "your-anthropic-api-key"
```

### 3. 執行

```bash
streamlit run app.py
```

瀏覽器會自動開啟 http://localhost:8501

## ☁️ 部署到 Streamlit Cloud

### 1. 上傳到 GitHub

將整個 `iching_webapp` 資料夾上傳到 GitHub repository。

### 2. 連結 Streamlit Cloud

1. 前往 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 帳號登入
3. 點擊 "New app"
4. 選擇您的 repository 和 `app.py`

### 3. 設定 Secrets

在 Streamlit Cloud 的 App settings → Secrets 中加入：

```toml
GEMINI_API_KEY = "your-gemini-api-key"
```

### 4. 部署完成

App 會自動部署，您會得到一個公開網址，例如：
`https://your-app-name.streamlit.app`

## 📁 目錄結構

```
iching_webapp/
├── app.py                  # Streamlit 主程式
├── requirements.txt        # Python 相依套件
├── README.md              # 本說明文件
├── .streamlit/
│   └── secrets.toml.example  # API Key 範例
└── iching_system/          # 易經占卜核心模組
    ├── core/               # 核心計算
    ├── divination/         # 起卦模組
    ├── interpretation/     # 解卦模組
    └── data/               # 卦象資料
```

## 📝 使用說明

### 手機使用

1. 開啟 App 網址
2. 選擇起卦方式
3. 依照指示輸入問題或回答問卷
4. 等待 30-60 秒取得結果
5. 展開各段落查看詳細解卦

### 結果說明

1. **現況**：目前的狀態
2. **變化趨勢**：未來的發展方向
3. **變化過程**：過渡期會面臨的情境
4. **各階段境遇**：六個階段的詳細描述
5. **建議**：具體可行的建議
6. **展望**：採取建議後的未來

## 🔧 開發

### 本地開發

```bash
# 安裝開發相依
pip install -r requirements.txt

# 執行（hot reload）
streamlit run app.py
```

### 修改 UI

編輯 `app.py` 中的 `st.markdown` 樣式區塊。

### 修改解卦邏輯

編輯 `iching_system/interpretation/interpreter.py`。

## 📄 授權

MIT License

## 👤 作者

Vincent Hsieh
