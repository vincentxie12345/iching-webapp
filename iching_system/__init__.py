# iching_system/__init__.py
"""
易經占卜系統
============

一個模組化的易經占卜系統，支援多種起卦方式和統一的解卦模組。

架構：
    Part 1 - 起卦：A1(隨機)/A2(報數)/A3(問卷)/A4(Agent)
    Part 2 - 計算：compute_b_stage
    Part 3 - 解卦：interpret

快速開始：
    >>> from iching_system import quick_divination
    >>> result = quick_divination("該不該跳槽？")

進階使用：
    >>> from iching_system import divination
    >>> result = divination("該不該跳槽？", method='A3')
"""

__version__ = '2.0.0'
__author__ = 'Vincent Hsieh'

# 主要入口
from .main import (
    divination,
    quick_divination,
    questionnaire,
    agent,
    init
)

# 核心模組
from .core import (
    dayan_six_yao,
    compute_b_stage,
    score_to_yao,
    get_hexagram,
    get_original_text
)

# 起卦模組
from .divination import (
    random_divination,
    number_divination,
    questionnaire_divination,
    agent_divination_a4_1
)

# 解卦模組
from .interpretation import (
    interpret,
    quick_interpret
)

# 設定
from .config import (
    load_env,
    check_api_keys,
    setup_api_key
)

__all__ = [
    # 版本
    '__version__',
    
    # 主要入口
    'divination',
    'quick_divination',
    'questionnaire',
    'agent',
    'init',
    
    # 核心
    'dayan_six_yao',
    'compute_b_stage',
    'score_to_yao',
    'get_hexagram',
    'get_original_text',
    
    # 起卦
    'random_divination',
    'number_divination',
    'questionnaire_divination',
    'agent_divination_a4_1',
    
    # 解卦
    'interpret',
    'quick_interpret',
    
    # 設定
    'load_env',
    'check_api_keys',
    'setup_api_key'
]
