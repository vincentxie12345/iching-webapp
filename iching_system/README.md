# 易經占卜系統 v2.0

模組化的易經占卜系統，支援多種起卦方式和統一的解卦模組。

## 📁 目錄結構

```
iching_system/
├── core/                    # 核心模組
│   ├── dayan.py            # 大衍筮法
│   ├── calculator.py       # B 階段計算
│   └── data_loader.py      # 資料載入器
│
├── divination/             # 起卦模組
│   ├── a1_random.py        # A1 隨機起卦
│   ├── a2_number.py        # A2 報數起卦
│   ├── a3_questionnaire.py # A3 問卷起卦
│   └── a4_agent.py         # A4 Agent 起卦
│
├── interpretation/         # 解卦模組
│   └── interpreter.py      # 統一解卦器
│
├── data/                   # 資料檔案
│   ├── i_ching.json        # 原典
│   ├── i_ching_modern.json # Modern 1
│   └── i_ching_modern2.json # Modern 2（主要）
│
├── config/                 # 設定
│   └── env.py              # 環境變數管理
│
├── research/               # 進階研究
│
├── main.py                 # 主程式入口
├── notebook_helper.py      # Jupyter 輔助
└── README.md
```

## 🚀 快速開始

### 安裝

```bash
# 複製整個 iching_system 資料夾到您的專案目錄
cp -r iching_system /path/to/your/project/

# 複製資料檔案到 data 目錄
cp i_ching*.json /path/to/your/project/iching_system/data/
```

### 設定 API Keys

建立 `.env` 檔案：

```
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 使用

```python
from iching_system import quick_divination, questionnaire, agent

# A1 隨機起卦
result = quick_divination("該不該跳槽？")

# A3 問卷起卦
result = questionnaire("該不該跳槽？")

# A4 Agent 起卦
result = agent("該不該跳槽？")
```

### Jupyter Notebook

```python
# 載入系統
exec(open('iching_system/notebook_helper.py').read())

# 使用
result = quick_divination("該不該跳槽？")
```

## 📐 架構說明

### Part 1: 起卦

| 方式 | 描述 | 函數 |
|------|------|------|
| A1 | 隨機起卦 | `random_divination()` |
| A2 | 報數起卦 | `number_divination(number)` |
| A3 | 問卷起卦 | `questionnaire_divination(question)` |
| A4 | Agent 起卦 | `agent_divination_a4_1(question)` |

### Part 2: 計算

```python
from iching_system.core import compute_b_stage

# 輸入六爻值，輸出本卦、之卦、轉移卦
hexagrams = compute_b_stage([7, 8, 9, 6, 7, 8])
```

### Part 3: 解卦

```python
from iching_system.interpretation import interpret

# 統一解卦，輸出六點說明
result = interpret(question, hexagrams)
```

## 📊 六點說明

1. **現況** - 本卦的含義
2. **變化趨勢** - 本卦→之卦的變化
3. **變化過程** - 轉移卦的含義
4. **六爻境遇** - 六個階段的描述
5. **建議** - 具體可行的建議
6. **展望** - 之卦的含義

## 🔮 原典支援

```python
from iching_system.core import get_original_text

# 取得原典文本
original = get_original_text("111111")  # 乾卦
```

## 📝 版本歷史

- v2.0.0: 模組化重構
- v1.x: 開發版本

## 👤 作者

Vincent Hsieh
