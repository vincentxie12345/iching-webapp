import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib
import traceback
import random

# 設定路徑：確保程式能找到 iching_system 資料夾
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 全域變數用來檢查核心狀態
CORE_LOADED = False
LOAD_ERROR = ""
get_hexagram = None
compute_b_stage = None

# 嘗試引入核心模組
try:
    # 修正：直接匯入存在的函數，而不是不存在的 Class
    from iching_system.core.data_loader import get_hexagram
    from iching_system.core.calculator import compute_b_stage
    
    CORE_LOADED = True
    print("Core modules (data_loader, calculator) loaded successfully.")
except Exception as e:
    CORE_LOADED = False
    LOAD_ERROR = str(e)
    print(f"Failed to load core modules: {e}")

app = FastAPI(title="Yi Li Decision API", version="1.0.0")

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():
    if CORE_LOADED:
        return {"status": "Yi Li System Online", "mode": "Full Core Loaded"}
    else:
        return {"status": "System Warning", "error": f"Import Error: {LOAD_ERROR}"}

@app.post("/api/ask")
def ask_question(request: QuestionRequest):
    """
    接收問題 -> 轉化為卦象 -> 回傳結果
    """
    if not CORE_LOADED:
        raise HTTPException(status_code=500, detail=f"System Core Error: {LOAD_ERROR}")

    try:
        q_text = request.question
        
        # 1. 將問題轉化為隨機種子 (Deterministic)
        hash_val = int(hashlib.sha256(q_text.encode()).hexdigest(), 16)
        random.seed(hash_val)
        
        # 2. 模擬生成本卦 (產生 6 個爻，每個爻是 0 或 1)
        # 這裡我們生成一個 6 位數的二進制字串，例如 "101101"
        # 易經通常是初爻在字串左邊或右邊需確認，這裡先假設標準順序
        code_list = [str(random.randint(0, 1)) for _ in range(6)]
        hex_code = "".join(code_list)
        
        # 3. 呼叫核心功能：查表取得真實卦名！
        # 使用 data_loader 裡的 get_hexagram
        hex_info = get_hexagram(hex_code)
        
        # 取得卦名，如果查不到就顯示代碼
        hex_name = hex_info.get('name', f"Unknown-{hex_code}")
        
        # 4. 模擬動爻 (0-5, 6代表無動爻)
        changing_line = hash_val % 7 
        
        # 5. 組裝回傳資料
        return {
            "question": q_text,
            "hexagram": {
                "code": hex_code,
                "name": hex_name,  # 這是真的從您資料庫查出來的名字！
                "changing": changing_line if changing_line < 6 else None
            },
            "waveform": {
                # 這些參數未來可以從 hex_info 裡面讀取 modern2 的參數
                "amplitude": 0.5 + (int(hex_code, 2) / 64.0),
                "frequency": 1.2
            },
            "interpretation": {
                "text": f"【核心運作中】您抽到了「{hex_name}」。(來自 iching_system 的真實資料)"
            }
        }

    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"Runtime Error: {error_msg}")
        raise HTTPException(status_code=500, detail=str(e))