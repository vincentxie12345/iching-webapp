# iching_system/notebook_helper.py
"""
Jupyter Notebook 快速啟動腳本
============================

在 Notebook 中執行：
    exec(open('iching_system/notebook_helper.py').read())
"""

import sys
import os
from pathlib import Path

# 自動偵測並設定路徑
def _setup_path():
    """設定系統路徑"""
    possible_paths = [
        Path.cwd(),
        Path.cwd().parent,
        Path.home() / 'pyprogram',
        Path('/mnt/project')
    ]
    
    for path in possible_paths:
        iching_path = path / 'iching_system'
        if iching_path.exists():
            if str(path) not in sys.path:
                sys.path.insert(0, str(path))
            return path
    
    return Path.cwd()

PROJECT_PATH = _setup_path()

# 載入環境變數
try:
    from dotenv import load_dotenv
    env_file = PROJECT_PATH / '.env'
    if env_file.exists():
        load_dotenv(env_file, override=True)
except ImportError:
    pass

# 匯入系統
try:
    from iching_system import (
        divination,
        quick_divination,
        questionnaire,
        agent,
        init,
        check_api_keys
    )
    
    from iching_system.core import (
        dayan_six_yao,
        compute_b_stage,
        score_to_yao,
        get_hexagram,
        clear_cache
    )
    
    # 清除快取確保重新載入資料
    clear_cache()
    
    print("✅ 易經占卜系統已載入")

except ImportError as e:
    print(f"❌ 匯入失敗: {e}")
