# iching_system/core/__init__.py
"""
易經核心模組
============

包含：
- dayan: 大衍筮法
- calculator: B 階段計算
- data_loader: 資料載入
"""

from .dayan import (
    dayan_six_yao,
    yao_to_bit,
    bits_to_code,
    code_to_bits,
    is_moving_line,
    get_moving_lines,
    flip_line,
    score_to_yao,
    get_yao_name,
    YAO_NAMES
)

from .calculator import (
    compute_b_stage,
    compute_now_code,
    compute_target_code,
    compute_transition_code,
    calculate_all_changes,
    get_hexagram_relationship
)

from .data_loader import (
    load_data,
    get_hexagram,
    get_hexagram_by_name,
    get_original_text,
    get_line_text,
    get_all_hexagram_codes,
    set_data_dir,
    hex_by_code,
    hex_original,
    clear_cache
)

__all__ = [
    # dayan
    'dayan_six_yao',
    'yao_to_bit',
    'bits_to_code',
    'code_to_bits',
    'is_moving_line',
    'get_moving_lines',
    'flip_line',
    'score_to_yao',
    'get_yao_name',
    'YAO_NAMES',
    
    # calculator
    'compute_b_stage',
    'compute_now_code',
    'compute_target_code',
    'compute_transition_code',
    'calculate_all_changes',
    'get_hexagram_relationship',
    
    # data_loader
    'load_data',
    'get_hexagram',
    'get_hexagram_by_name',
    'get_original_text',
    'get_line_text',
    'get_all_hexagram_codes',
    'set_data_dir',
    'hex_by_code',
    'hex_original',
    'clear_cache'
]
