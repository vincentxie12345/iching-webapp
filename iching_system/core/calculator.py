# iching_system/core/calculator.py
"""
B 階段計算
==========
計算本卦、之卦、轉移卦

核心邏輯：
- 本卦：六爻的當前狀態
- 之卦：動爻變化後的狀態
- 轉移卦：變化過程的中間狀態
"""

from typing import List, Dict, Tuple
from .dayan import (
    yao_to_bit, 
    bits_to_code, 
    code_to_bits,
    is_moving_line, 
    get_moving_lines,
    flip_bit,
    flip_line
)
from .data_loader import get_hexagram


def compute_now_code(yao_values: List[int]) -> str:
    """
    計算本卦卦碼
    
    Args:
        yao_values: 六爻值 [6/7/8/9 × 6]
    
    Returns:
        本卦卦碼（如 "111111"）
    """
    bits = [yao_to_bit(y) for y in yao_values]
    return bits_to_code(bits)


def compute_target_code(yao_values: List[int]) -> str:
    """
    計算之卦卦碼（動爻翻轉）
    
    Args:
        yao_values: 六爻值 [6/7/8/9 × 6]
    
    Returns:
        之卦卦碼
    """
    bits = []
    for y in yao_values:
        bit = yao_to_bit(y)
        if is_moving_line(y):
            bit = flip_bit(bit)
        bits.append(bit)
    return bits_to_code(bits)


def start_index(yao_values: List[int]) -> int:
    """
    計算起始爻位索引
    
    根據動爻數量決定起始點：
    - 0 動爻：從初爻開始
    - 1 動爻：從該動爻開始
    - 2+ 動爻：從最低動爻開始
    """
    moving = get_moving_lines(yao_values)
    if not moving:
        return 0
    return min(moving)


def compute_transition_code(yao_values: List[int], now_code: str, target_code: str) -> str:
    """
    計算轉移卦卦碼
    
    轉移卦代表變化過程中的狀態
    """
    moving = get_moving_lines(yao_values)
    
    if not moving:
        # 無動爻，轉移卦等於本卦
        return now_code
    
    # 計算轉移卦
    n_moving = len(moving)
    now_bits = code_to_bits(now_code)
    target_bits = code_to_bits(target_code)
    
    if n_moving == 1:
        # 單動爻：轉移卦 = 之卦
        return target_code
    
    elif n_moving == 2:
        # 雙動爻：翻轉第一個動爻
        trans_bits = now_bits.copy()
        trans_bits[moving[0]] = flip_bit(trans_bits[moving[0]])
        return bits_to_code(trans_bits)
    
    elif n_moving == 3:
        # 三動爻：看內外卦
        # 如果動爻在內卦（0,1,2），翻轉內卦動爻
        # 如果動爻在外卦（3,4,5），翻轉外卦動爻
        inner_moving = [m for m in moving if m < 3]
        outer_moving = [m for m in moving if m >= 3]
        
        trans_bits = now_bits.copy()
        if len(inner_moving) >= len(outer_moving):
            for m in inner_moving:
                trans_bits[m] = flip_bit(trans_bits[m])
        else:
            for m in outer_moving:
                trans_bits[m] = flip_bit(trans_bits[m])
        return bits_to_code(trans_bits)
    
    else:
        # 4+ 動爻：複雜情況，用中間狀態
        trans_bits = now_bits.copy()
        half = n_moving // 2
        for i in range(half):
            m = moving[i]
            trans_bits[m] = flip_bit(trans_bits[m])
        return bits_to_code(trans_bits)


def compute_b_stage(yao_values: List[int]) -> Dict:
    """
    計算 B 階段（核心函數）
    
    Args:
        yao_values: 六爻值 [6/7/8/9 × 6]
    
    Returns:
        {
            '本卦': {'code': '...', 'name': '...', ...},
            '之卦': {'code': '...', 'name': '...', ...},
            '轉移卦': {'code': '...', 'name': '...', ...},
            '動爻': [0, 3, ...],
            '動爻數': 2,
            'yao_values': [7, 8, 9, 6, 7, 8]
        }
    """
    # 計算卦碼
    now_code = compute_now_code(yao_values)
    target_code = compute_target_code(yao_values)
    trans_code = compute_transition_code(yao_values, now_code, target_code)
    
    # 取得動爻
    moving = get_moving_lines(yao_values)
    
    # 取得卦象資料
    hex_now = get_hexagram(now_code)
    hex_target = get_hexagram(target_code)
    hex_trans = get_hexagram(trans_code)
    
    # 補充 code 欄位（如果沒有）
    if 'code' not in hex_now:
        hex_now['code'] = now_code
    if 'code' not in hex_target:
        hex_target['code'] = target_code
    if 'code' not in hex_trans:
        hex_trans['code'] = trans_code
    
    return {
        '本卦': hex_now,
        '之卦': hex_target,
        '轉移卦': hex_trans,
        '動爻': moving,
        '動爻數': len(moving),
        'yao_values': yao_values
    }


def calculate_all_changes(now_code: str) -> List[Dict]:
    """
    計算本卦所有可能的變化路徑
    
    Args:
        now_code: 本卦卦碼
    
    Returns:
        所有可能的變化列表
    """
    results = []
    
    for i in range(6):
        target_code = flip_line(now_code, i)
        
        results.append({
            'line_index': i,
            'now_code': now_code,
            'target_code': target_code,
            'now_hex': get_hexagram(now_code),
            'target_hex': get_hexagram(target_code)
        })
    
    return results


def get_hexagram_relationship(code1: str, code2: str) -> Dict:
    """
    分析兩卦之間的關係
    
    Args:
        code1: 第一卦卦碼
        code2: 第二卦卦碼
    
    Returns:
        關係分析
    """
    bits1 = code_to_bits(code1)
    bits2 = code_to_bits(code2)
    
    # 計算差異爻位
    diff_lines = [i for i in range(6) if bits1[i] != bits2[i]]
    
    # 計算內外卦差異
    inner_diff = sum(1 for i in range(3) if bits1[i] != bits2[i])
    outer_diff = sum(1 for i in range(3, 6) if bits1[i] != bits2[i])
    
    # 計算陰陽比例
    yang1 = sum(bits1)
    yang2 = sum(bits2)
    
    return {
        'diff_lines': diff_lines,
        'diff_count': len(diff_lines),
        'inner_diff': inner_diff,
        'outer_diff': outer_diff,
        'yang_change': yang2 - yang1,
        'hex1_yang': yang1,
        'hex2_yang': yang2
    }
